from collections.abc import Callable
from typing import NamedTuple, TYPE_CHECKING

if TYPE_CHECKING:
    from src.loop import Loop


class Callback[*Ts](NamedTuple):
    func: Callable[['Loop', *Ts], None]
    args: tuple[*Ts] = ()
