import socket

from src.callback import Callback
from src.condition import IOCondition, IOConditionKind, TimeCondition
from src.loop import Loop


def on_socket_read(
    loop: Loop,
    idx: int,
    sock: socket.socket,
    started_at: float
) -> None:
    data = sock.recv(1024)
    print(f'socket {idx=} elapsed={loop.time() - started_at} {data=}')
    sock.close()


def async_main(
    loop: Loop
) -> None:
    loop.add_callback(
        TimeCondition(loop.time() + 1),
        Callback(print, ('one second passed',))
    )
    loop.add_callback(
        TimeCondition(loop.time() + 2),
        Callback(print, ('two seconds passed',))
    )

    started_at = loop.time()
    for i in range(2):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        sock.connect(('httpbin.org', 80))
        sock.sendall(b'GET /delay/3 HTTP/1.1\r\nHost: httpbin.org\r\n\r\n')
        loop.add_callback(
            IOCondition(sock.fileno(), IOConditionKind.READ),
            Callback(on_socket_read, (i, sock, started_at))
        )


def main() -> None:
    loop = Loop()
    loop.add_callback(
        TimeCondition(loop.time()),
        Callback(async_main)
    )
    loop.run()


if __name__ == '__main__':
    main()
