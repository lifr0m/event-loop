import socket

from src.condition import IOCondition, IOConditionKind
from src.coroutine import Coroutine
from src.loop import Loop


def read_data(
    sock: socket.socket
) -> Coroutine[bytes]:
    yield IOCondition(sock.fileno(), IOConditionKind.READ)
    return sock.recv(4096)


def async_main(
    loop: Loop,
    idx: int,
    started_at: float
) -> Coroutine:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    try:
        sock.connect(('httpbin.org', 80))
        sock.sendall(b'GET /delay/3 HTTP/1.1\r\nHost: httpbin.org\r\n\r\n')
        data = yield from read_data(sock)
        print(f'{idx=} elapsed={loop.time() - started_at} {data=}')
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
