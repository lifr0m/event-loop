import contextlib
import socket

from src.condition import IOCondition, IOConditionKind
from src.coroutine import Coroutine
from src.loop import Loop


def write_data(
    sock: socket.socket,
    data: bytes
) -> Coroutine[None]:
    yield IOCondition(sock.fileno(), IOConditionKind.WRITE)
    sock.sendall(data)


def read_data(
    sock: socket.socket
) -> Coroutine[bytes]:
    yield IOCondition(sock.fileno(), IOConditionKind.READ)
    return sock.recv(2 ** 16)


def async_main(
    loop: Loop,
    idx: int,
    started_at: float
) -> Coroutine[None]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    sock.setblocking(False)
    try:
        with contextlib.suppress(BlockingIOError):
            sock.connect(('httpbin.org', 80))

        data = b'GET /delay/3 HTTP/1.1\r\nHost: httpbin.org\r\n\r\n'
        yield from write_data(sock, data)

        resp = yield from read_data(sock)
        elapsed = loop.time() - started_at

        print(f'{idx=} {elapsed=} {resp=}')
    finally:
        sock.close()


def main() -> None:
    loop = Loop()
    started_at = loop.time()
    for idx in range(2):
        loop.schedule_soon(async_main(loop, idx, started_at))
    loop.run()


if __name__ == '__main__':
    main()
