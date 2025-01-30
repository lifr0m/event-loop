import select
import time

from src.condition import Condition, IOCondition, IOConditionKind, TimeCondition
from src.coroutine import Coroutine


MAX_TIMEOUT = 60.0


class Loop:

    def __init__(self) -> None:
        self._coroutines: dict[Condition, list[Coroutine]] = {}
        self._running = False

    def time(self) -> float:
        return time.monotonic()

    def schedule(self,
        cond: Condition,
        coro: Coroutine
    ) -> None:
        self._coroutines.setdefault(cond, [])
        self._coroutines[cond].append(coro)

    def schedule_at(self,
        when: float,
        coro: Coroutine
    ) -> None:
        self.schedule(TimeCondition(when), coro)

    def schedule_later(self,
        delay: float,
        coro: Coroutine
    ) -> None:
        self.schedule_at(self.time() + delay, coro)

    def schedule_soon(self,
        coro: Coroutine
    ) -> None:
        self.schedule_later(0, coro)

    def run(self) -> None:
        if self._running:
            raise RuntimeError('loop is already running')

        self._running = True
        try:
            while self._coroutines:
                self._run_once()
        finally:
            self._running = False

    def _run_once(self) -> None:
        r_set = set()
        w_set = set()
        x_set = set()
        timeout = MAX_TIMEOUT
        for cond in self._coroutines:
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

        r_list, w_list, x_list = select.select(r_set, w_set, x_set, timeout)
        if x_list:
            raise RuntimeError(f'exceptional condition: {x_list}')

        time_ready = [
            (cond, coro)
            for cond, coro_list in self._coroutines.items()
            if isinstance(cond, TimeCondition)
            if cond.when <= self.time()
            for coro in coro_list
        ]
        io_ready = [
            (IOCondition(fd, kind), coro)
            for fd_list, kind in [
                (r_list, IOConditionKind.READ),
                (w_list, IOConditionKind.WRITE),
            ]
            for fd in fd_list
            for coro in self._coroutines[IOCondition(fd, kind)]
        ]
        ready = time_ready + io_ready

        for cond, coro in ready:
            self._coroutines[cond].remove(coro)
            if not self._coroutines[cond]:
                self._coroutines.pop(cond)

            try:
                next_cond = coro.send(None)
            except StopIteration:
                pass
            else:
                self.schedule(next_cond, coro)
