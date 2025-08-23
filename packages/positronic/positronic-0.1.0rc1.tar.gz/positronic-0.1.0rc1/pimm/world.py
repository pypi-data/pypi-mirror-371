"""Implementation of multiprocessing channels."""

from collections import deque
import heapq
import logging
import multiprocessing as mp
import multiprocessing.shared_memory
import multiprocessing.managers as mp_managers
from multiprocessing.synchronize import Event as EventClass

import sys
from queue import Empty, Full
import time
import traceback
from typing import Iterator, Sequence, Tuple, TypeVar

from .core import Clock, ControlLoop, Message, SignalEmitter, SignalReader, Sleep
from .shared_memory import SMCompliant, SharedMemoryEmitter, SharedMemoryReader


T = TypeVar('T')
T_SM = TypeVar('T_SM', bound=SMCompliant)


class QueueEmitter(SignalEmitter[T]):
    def __init__(self, queue: mp.Queue, clock: Clock):
        self._queue = queue
        self._clock = clock

    def emit(self, data: T, ts: int = -1) -> bool:
        ts = ts if ts >= 0 else self._clock.now_ns()
        try:
            self._queue.put_nowait(Message(data, ts))
            return True
        except Full:
            # Queue is full, try to remove old message and try again
            try:
                self._queue.get_nowait()
                self._queue.put_nowait(Message(data, ts))
                return True
            except (Empty, Full):
                return False


class BroadcastEmitter(SignalEmitter[T]):
    def __init__(self, emitters: Sequence[SignalEmitter[T]]):
        """Emitter that broadcasts messages to all emmiters.

        Args:
            emitters: (Sequence[SignalEmitter]) Emitters to broadcast to.
        """
        self._emitters = emitters

    def emit(self, data: T, ts: int = -1) -> bool:
        any_failed = False
        for emitter in self._emitters:
            any_failed = any_failed or not emitter.emit(data, ts)
        return not any_failed


class QueueReader(SignalReader[T]):
    def __init__(self, queue: mp.Queue):
        self._queue = queue
        self._last_value = None

    def read(self) -> Message[T] | None:
        try:
            self._last_value = self._queue.get_nowait()
        except Empty:
            pass
        return self._last_value


class LocalQueueEmitter(SignalEmitter[T]):
    def __init__(self, queue: deque, clock: Clock):
        """Emitter that allows to emit messages to deque.

        Args:
            queue: (deque) Queue to emit to.
            clock: (Clock) Clock to use for timestamps.
        """
        self._queue = queue
        self._clock = clock

    def emit(self, data: T, ts: int = -1) -> bool:
        self._queue.append(Message(data, ts if ts >= 0 else self._clock.now_ns()))
        return True


class LocalQueueReader(SignalReader[T]):
    def __init__(self, queue: deque):
        """Reader that allows to read messages from deque.

        Args:
            queue: (deque) Queue to read from.
        """
        self._queue = queue
        self._last_value = None

    def read(self) -> Message[T] | None:
        if len(self._queue) > 0:
            self._last_value = self._queue.popleft()

        return self._last_value


class EventReader(SignalReader[bool]):
    def __init__(self, event: EventClass, clock: Clock):
        self._event = event
        self._clock = clock

    def read(self) -> Message[bool] | None:
        return Message(data=self._event.is_set(), ts=self._clock.now_ns())


class SystemClock(Clock):
    def now(self) -> float:
        return time.monotonic()

    def now_ns(self) -> int:
        return time.monotonic_ns()


def _bg_wrapper(run_func: ControlLoop, stop_event: EventClass, clock: Clock, name: str):
    try:
        for command in run_func(EventReader(stop_event, clock), clock):
            match command:
                case Sleep(seconds):
                    time.sleep(seconds)
                case _:
                    raise ValueError(f"Unknown command: {command}")
    except KeyboardInterrupt:
        # Silently handle KeyboardInterrupt in background processes
        pass
    except Exception:
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"ERROR in background process '{name}':", file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        print(f"{'='*60}\n", file=sys.stderr)
        logging.error(f"Error in control system {name}:\n{traceback.format_exc()}")
    finally:
        print(f"Stopping background process by {name}", flush=True)
        stop_event.set()


class World:
    """Utility class to bind and run control loops."""

    def __init__(self, clock: Clock = SystemClock()):
        # TODO: stop_signal should be a shared variable, since we should be able to track if background
        # processes are still running
        self._clock = clock

        self._stop_event = mp.Event()
        self.background_processes = []
        self._manager = mp.Manager()
        self._sm_manager = mp_managers.SharedMemoryManager()
        self._sm_emitters_readers = []
        self.entered = False

    def __enter__(self):
        self._sm_manager.__enter__()
        self.entered = True
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.entered = False
        print("Stopping background processes...", flush=True)
        self._stop_event.set()
        time.sleep(0.1)

        print(f"Waiting for {len(self.background_processes)} background processes to terminate...", flush=True)
        for process in self.background_processes:
            process.join(timeout=3)
            if process.is_alive():
                print(f'Process {process.name} (pid {process.pid}) did not respond, terminating...', flush=True)
                process.terminate()
                process.join(timeout=2)  # Give it a moment to terminate
                if process.is_alive():
                    print(f'Process {process.name} (pid {process.pid}) still alive, killing...', flush=True)
                    process.kill()
            print(f'Process {process.name} (pid {process.pid}) finished', flush=True)
            process.close()

        for emitter, reader in self._sm_emitters_readers:
            reader.close()
            emitter.close()

        self._sm_manager.__exit__(exc_type, exc_value, traceback)

    def local_pipe(self, maxsize: int = 1) -> Tuple[SignalEmitter[T], SignalReader[T]]:
        """Create a queue-based communication channel within the same process.

        Args:
            maxsize: (int) Maximum queue size (0 for unlimited). Default is 1.

        Returns:
            Tuple of (emitter, reader) for local communication
        """
        q = deque(maxlen=maxsize)
        return LocalQueueEmitter(q, self._clock), LocalQueueReader(q)

    def mp_pipe(self, maxsize: int = 1) -> Tuple[SignalEmitter[T], SignalReader[T]]:
        """Create a queue-based communication channel between processes.

        Args:
            maxsize: (int) Maximum queue size (0 for unlimited). Default is 1.

        Returns:
            Tuple of (emitter, reader) for inter-process communication
        """
        q = self._manager.Queue(maxsize=maxsize)

        return QueueEmitter(q, self._clock), QueueReader(q)  # type: ignore

    def local_one_to_many_pipe(
        self, n_readers: int,
        maxsize: int = 1
    ) -> Tuple[SignalEmitter[T], Sequence[SignalReader[T]]]:
        """Create a single-emitter-many-readers communication channel.
        """
        emitters = []
        readers = []
        for _ in range(n_readers):
            emitter, reader = self.local_pipe(maxsize)
            emitters.append(emitter)
            readers.append(reader)
        return BroadcastEmitter(emitters), readers

    def mp_one_to_many_pipe(
        self,
        n_readers: int,
        maxsize: int = 1
    ) -> Tuple[SignalEmitter[T], Sequence[SignalReader[T]]]:
        """Create a single-emitter-many-readers communication channel.

        Args:
            n_readers: (int) Number of readers to create
            maxsize: (int) Maximum queue size (0 for unlimited)

        Returns:
            Tuple of (emitter, readers) for single-emitter-many-readers communication
        """
        readers = []
        emitters = []
        for _ in range(n_readers):
            emiter, reader = self.mp_pipe(maxsize)
            readers.append(reader)
            emitters.append(emiter)
        return BroadcastEmitter(emitters), readers

    def shared_memory(self) -> Tuple[SignalEmitter[T_SM], SignalReader[T_SM]]:
        """Create shared memory channel for efficient data sharing.

        Message data must be a SMCompliant type and have the same buffer size as the first message emitted.

        Args:
            data_type: SMCompliant type that defines the shared data structure

        Returns:
            Tuple of (emitter, reader) for shared memory inter-process communication
        """
        assert self.entered, "Shared memory is only available after entering the world context."
        lock = self._manager.Lock()
        ts_value = self._manager.Value('Q', -1)
        sm_queue = self._manager.Queue()
        emitter = SharedMemoryEmitter(lock, ts_value, sm_queue, self._clock)
        reader = SharedMemoryReader(lock, ts_value, sm_queue)
        self._sm_emitters_readers.append((emitter, reader))
        return emitter, reader

    def start_in_subprocess(self, *background_loops: ControlLoop):
        """Starts background control loops. Can be called multiple times for different control loops."""
        for bg_loop in background_loops:
            if hasattr(bg_loop, '__self__'):
                name = f"{bg_loop.__self__.__class__.__name__}.{bg_loop.__name__}"
            else:
                name = getattr(bg_loop, '__name__', 'anonymous')
            # TODO: now we allow only real clock, change clock to a Emitter?
            p = mp.Process(target=_bg_wrapper,
                           args=(bg_loop, self._stop_event, SystemClock(), name),
                           daemon=True,
                           name=name)
            p.start()
            self.background_processes.append(p)
            print(f"Started background process {name} (pid {p.pid})", flush=True)

    @property
    def should_stop(self) -> bool:
        return self._stop_event.is_set()

    def should_stop_reader(self) -> SignalReader[bool]:
        return EventReader(self._stop_event, self._clock)

    def interleave(self, *loops: ControlLoop) -> Iterator[Sleep]:
        """Interleave multiple control loops, scheduling them based on their timing requirements.

        This method runs multiple control loops concurrently by executing the next scheduled
        loop and then yielding the wait time until the next execution should occur.

        Args:
            *loops: Variable number of control loops to interleave

        Yields:
            float: Wait times until the next scheduled execution should occur

        Behavior:
            - All loops start at the same time
            - At each step: execute the next scheduled loop, then yield wait time
            - Loops are scheduled for future execution based on their yielded sleep times
            - When any loop completes (StopIteration), the stop event is set
            - Other loops can check the stop event and exit early if desired
            - The method continues until all loops have completed
            - Number of yields equals number of loop executions
        """
        start = self._clock.now()
        counter = 0
        priority_queue = []

        # Initialize all loops with the same start time and unique counters
        for loop in loops:
            priority_queue.append((start, counter, iter(loop(self.should_stop_reader(), self._clock))))
            counter += 1

        heapq.heapify(priority_queue)

        while priority_queue:
            _, _, loop = heapq.heappop(priority_queue)

            try:
                sleep_time = next(loop).seconds
                heapq.heappush(priority_queue, (self._clock.now() + sleep_time, counter, loop))
                counter += 1

                if priority_queue:  # Yield the wait time until the next execution should occur
                    yield Sleep(max(0, priority_queue[0][0] - self._clock.now()))

            except StopIteration:
                # Don't add the loop back and don't yield after a loop completes - it is done
                self._stop_event.set()

    def run(self, *loops: ControlLoop):
        for command in self.interleave(*loops):
            match command:
                case Sleep(seconds):
                    time.sleep(seconds)
                case _:
                    raise ValueError(f"Unknown command: {command}")
