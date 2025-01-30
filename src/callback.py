from collections.abc import Callable
from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    from src.loop import Loop


Callback: TypeAlias = Callable[['Loop'], None]
