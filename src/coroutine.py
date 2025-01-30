from collections.abc import Iterator
from typing import TypeAlias

from src.condition import Condition


Coroutine: TypeAlias = Iterator[Condition]
