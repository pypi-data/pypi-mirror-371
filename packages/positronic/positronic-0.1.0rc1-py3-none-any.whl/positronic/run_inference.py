from typing import Any, Iterator, Mapping, Sequence

import numpy as np
import tqdm
import rerun as rr
import torch

import configuronic as cfn
import pimm
from positronic.drivers import roboarm
from positronic.drivers.camera.linux_video import LinuxVideo
from positronic.drivers.gripper.dh import DHGripper
from positronic.simulator.mujoco.sim import MujocoCamera, MujocoFranka, MujocoGripper, MujocoSim
from positronic.inference.action import ActionDecoder
from positronic.inference.state import StateEncoder
from positronic.simulator.mujoco.transforms import MujocoSceneTransform

import positronic.cfg.hardware.roboarm
import positronic.cfg.hardware.gripper
import positronic.cfg.hardware.camera
import positronic.cfg.simulator
import positronic.cfg.inference.state


def rerun_log_observation(ts, obs):
    rr.set_time('time', duration=ts)

    def log_image(name, tensor, compress: bool = True):
        tensor = tensor.squeeze(0)
        tensor = (tensor * 255).type(torch.uint8)
        tensor = tensor.permute(1, 2, 0).cpu().numpy()
        rr_img = rr.Image(tensor)
        if compress:
            rr_img = rr_img.compress()
        rr.log(name, rr_img)

    for k, v in obs.items():
        if k.startswith("observation.images."):
            log_image(k, v)

    for i, state in enumerate(obs['observation.state'].squeeze(0)):
        rr.log(f"observation/state/{i}", rr.Scalar(state.item()))


def rerun_log_action(ts, action):
    rr.set_time('time', duration=ts)
    for i, action in enumerate(action):
        rr.log(f"action/{i}", rr.Scalars(action))


class Inference:
    frames : dict[str, pimm.SignalReader[Mapping[str, np.ndarray]]] = {}
    robot_state : pimm.SignalReader[roboarm.State] = pimm.NoOpReader()
    gripper_state : pimm.SignalReader[float] = pimm.NoOpReader()

    robot_commands : pimm.SignalEmitter[roboarm.command.CommandType] = pimm.NoOpEmitter()
    target_grip : pimm.SignalEmitter[float] = pimm.NoOpEmitter()

    def __init__(
        self,
        state_encoder: StateEncoder,
        action_decoder: ActionDecoder,
        device: str,
        policy,
        rerun_path: str | None = None,
        inference_fps: int = 30,
    ):
        self.state_encoder = state_encoder
        self.action_decoder = action_decoder
        self.policy = policy.to(device)
        self.device = device
        self.rerun_path = rerun_path
        self.inference_fps = inference_fps

    def run(self, should_stop: pimm.SignalReader, clock: pimm.Clock) -> Iterator[pimm.Sleep]:  # noqa: C901
        frames = {
            camera_name: pimm.DefaultReader(frame, {})
            for camera_name, frame in self.frames.items()
        }

        reference_pose = None
        rate_limiter = pimm.RateLimiter(clock, hz=self.inference_fps)

        if self.rerun_path:
            rr.init("inference")
            rr.save(self.rerun_path)

        while not should_stop.value:
            frame_messages = {k: v.read() for k, v in frames.items()}
            if not all('image' in v.data for v in frame_messages.values()):
                yield pimm.Sleep(0.001)
                continue

            images = {f"{k}.image": v.data['image'] for k, v in frame_messages.items()}

            robot_state = self.robot_state.read()
            if robot_state is None:
                yield pimm.Sleep(0.001)
                continue

            gripper_state = self.gripper_state.read()
            if gripper_state is None:
                yield pimm.Sleep(0.001)
                continue

            robot_state = robot_state.data

            if robot_state.status == roboarm.RobotStatus.MOVING:
                # TODO: seems to be necessary to wait previous command to finish
                yield pimm.Sleep(0.001)
                continue

            if reference_pose is None:
                reference_pose = robot_state.ee_pose.copy()

            inputs = {
                'robot_position_translation': robot_state.ee_pose.translation,
                'robot_position_rotation': robot_state.ee_pose.rotation.as_quat,
                'robot_joints': robot_state.q,
                'grip': gripper_state.data,
                'reference_robot_position_translation': reference_pose.translation,
                'reference_robot_position_quaternion': reference_pose.rotation.as_quat
            }
            obs = self.state_encoder.encode(images, inputs)
            for key in obs:
                obs[key] = obs[key].to(self.device)

            action = self.policy.select_action(obs).squeeze(0).cpu().numpy()
            action_dict = self.action_decoder.decode(action, inputs)
            target_pos = action_dict['target_robot_position']

            roboarm_command = roboarm.command.CartesianMove(pose=target_pos)

            # TODO: this should be inside the policy
            if self.policy.chunk_start():
                reference_pose = target_pos

            self.robot_commands.emit(roboarm_command)
            self.target_grip.emit(action_dict['target_grip'].item())

            if self.rerun_path:
                rerun_log_observation(clock.now(), obs)
                rerun_log_action(clock.now(), action)

            yield pimm.Sleep(rate_limiter.wait_time())


def main(robot_arm: Any | None,
         gripper: DHGripper | None,
         cameras: Mapping[str, LinuxVideo] | None,
         state_encoder: StateEncoder,
         action_decoder: ActionDecoder,
         policy,
         rerun_path: str | None = None,
         device: str = 'cuda',
         ):

    with pimm.World() as world:
        inference = Inference(state_encoder, action_decoder, device, policy, rerun_path)
        cameras = cameras or {}
        for camera_name, camera in cameras.items():
            camera.frame, inference.frames[camera_name] = world.mp_pipe()

        world.start_in_subprocess(*[camera.run for camera in cameras.values()])

        if robot_arm is not None:
            robot_arm.state, inference.robot_state = world.shared_memory()
            inference.robot_commands, robot_arm.commands = world.mp_pipe()
            world.start_in_subprocess(robot_arm.run)

        if gripper is not None:
            inference.target_grip, gripper.target_grip = world.mp_pipe()
            gripper.grip, inference.gripper_state = world.mp_pipe()
            world.start_in_subprocess(gripper.run)

        world.run(inference.run)


def main_sim(
        mujoco_model_path: str,
        state_encoder: StateEncoder,
        action_decoder: ActionDecoder,
        policy,
        rerun_path: str,
        loaders: Sequence[MujocoSceneTransform],
        fps: int,
        device: str,
        simulation_time: float,
):
    sim = MujocoSim(mujoco_model_path, loaders)
    robot_arm = MujocoFranka(sim, suffix='_ph')
    cameras = {
        'image.back': MujocoCamera(sim.model, sim.data, 'handcam_back_ph', (1280, 720), fps=fps),
        'image.front': MujocoCamera(sim.model, sim.data, 'handcam_front_ph', (1280, 720), fps=fps),
    }
    gripper = MujocoGripper(sim, actuator_name='actuator8_ph', joint_name='finger_joint1_ph')
    inference = Inference(state_encoder, action_decoder, device, policy, rerun_path)

    with pimm.World(clock=sim) as world:
        cameras = cameras or {}
        for camera_name, camera in cameras.items():
            camera.frame, inference.frames[camera_name] = world.local_pipe()

        robot_arm.state, inference.robot_state = world.local_pipe()
        inference.robot_commands, robot_arm.commands = world.local_pipe()
        gripper.grip, inference.gripper_state = world.local_pipe()

        inference.target_grip, gripper.target_grip = world.local_pipe()

        sim_iter = world.interleave(
            sim.run,
            *[camera.run for camera in cameras.values()],
            robot_arm.run,
            gripper.run,
            inference.run,
        )

        p_bar = tqdm.tqdm(total=simulation_time, unit='s')
        for _ in sim_iter:
            p_bar.n = round(sim.now(), 1)
            p_bar.refresh()
            if sim.now() > simulation_time:
                break


main_cfg = cfn.Config(
    main,
    robot_arm=positronic.cfg.hardware.roboarm.kinova,
    gripper=positronic.cfg.hardware.gripper.dh_gripper,
    state_encoder=positronic.cfg.inference.state.end_effector_224,
    action_decoder=positronic.cfg.inference.action.umi_relative,
    policy=positronic.cfg.inference.policy.act,
    cameras={
        'left': positronic.cfg.hardware.camera.arducam_left,
        'right': positronic.cfg.hardware.camera.arducam_right,
    },
    rerun_path="inference.rrd",
    device='cuda',
)


main_sim_cfg = cfn.Config(
    main_sim,
    mujoco_model_path="positronic/assets/mujoco/franka_table.xml",
    loaders=positronic.cfg.simulator.stack_cubes_loaders,
    state_encoder=positronic.cfg.inference.state.end_effector_back_front,
    action_decoder=positronic.cfg.inference.action.relative_robot_position,
    policy=positronic.cfg.inference.policy.act,
    rerun_path="inference.rrd",
    fps=60,
    device='cuda',
    simulation_time=10,
)

if __name__ == "__main__":
    cfn.cli({
        "real": main_cfg,
        "sim": main_sim_cfg,
    })
