import enum
import select
import time

from .callback import Callback
from .condition import Condition, IOCondition, IOConditionKind, TimeCondition


MAX_TIMEOUT = 60.0


class State(enum.Enum):
    STOPPED = 'stopped'
    RUNNING = 'running'


class Loop:

    def __init__(self) -> None:
        self._state = State.STOPPED
        self._callbacks: dict[Condition, list[Callback]] = {}

    def time(self) -> float:
        return time.monotonic()

    def is_running(self) -> bool:
        return self._state == State.RUNNING

    def add_callback(self,
        condition: Condition,
        callback: Callback
    ) -> None:
        self._callbacks.setdefault(condition, [])
        self._callbacks[condition].append(callback)

    def run(self) -> None:
        if self.is_running():
            raise RuntimeError('loop is already running')

        self._state = State.RUNNING
        try:
            while self._callbacks:
                self._run_once()
        finally:
            self._state = State.STOPPED

    def _run_once(self) -> None:
        r_set = set()
        w_set = set()
        x_set = set()
        timeout = MAX_TIMEOUT
        for cond in self._callbacks:
            if isinstance(cond, TimeCondition):
                delay = max(0.0, cond.when - self.time())
                timeout = min(timeout, delay)
            elif isinstance(cond, IOCondition):
                if cond.kind == IOConditionKind.READ:
                    r_set.add(cond.fd)
                elif cond.kind == IOConditionKind.WRITE:
                    w_set.add(cond.fd)
                else:
                    raise RuntimeError(f'unknown IO condition kind: {cond.kind}')
                x_set.add(cond.fd)
            else:
                raise RuntimeError(f'unknown condition: {cond}')

        r_list, w_list, x_list = select.select(
            list(r_set), list(w_set), list(x_set), timeout
        )
        if x_list:
            raise RuntimeError(f'exceptional condition: {x_list}')

        for cond, cb in [
            (cond, cb)
            for cond, cb_list in self._callbacks.items()
            if isinstance(cond, TimeCondition)
            if cond.when <= self.time()
            for cb in cb_list
        ] + [
            (IOCondition(fd, kind), cb)
            for fd_list, kind in [
                (r_list, IOConditionKind.READ),
                (w_list, IOConditionKind.WRITE),
            ]
            for fd in fd_list
            for cb in self._callbacks[IOCondition(fd, kind)]
        ]:
            self._callbacks[cond].remove(cb)
            if not self._callbacks[cond]:
                self._callbacks.pop(cond)
            cb(self)
