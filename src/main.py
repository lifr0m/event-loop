from src.condition import IOCondition, IOConditionKind, TimeCondition
from src.loop import Loop


def on_stdout_write_ready(
    loop: Loop
) -> None:
    print('stdout is ready for writing!')

    loop.add_callback(
        TimeCondition(loop.time() + 1),
        lambda loop: print('one second passed')
    )
    loop.add_callback(
        TimeCondition(loop.time() + 2),
        lambda loop: print('two seconds passed')
    )


def async_main(
    loop: Loop
) -> None:
    print('running async main')

    loop.add_callback(
        IOCondition(1, IOConditionKind.WRITE),
        on_stdout_write_ready
    )


def main() -> None:
    loop = Loop()
    loop.add_callback(
        TimeCondition(loop.time()),
        async_main
    )
    loop.run()


if __name__ == '__main__':
    main()
