from collections.abc import Generator

from src.condition import Condition


type Coroutine[T] = Generator[Condition, None, T]
