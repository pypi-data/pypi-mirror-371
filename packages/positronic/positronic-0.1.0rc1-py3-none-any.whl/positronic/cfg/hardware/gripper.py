import configuronic as cfn


@cfn.config(port="/dev/ttyUSB0")
def dh_gripper(port: str):
    from positronic.drivers.gripper.dh import DHGripper  # noqa: F401
    return DHGripper(port=port)


@cfn.config(ip="172.168.0.2")
def franka(ip: str):
    from positronic.drivers.gripper.franka import Gripper  # noqa: F401
    return Gripper(ip=ip)
