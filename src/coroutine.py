from collections.abc import Generator

from src.condition import Condition


type Coroutine[T = None] = Generator[Condition, None, T]
