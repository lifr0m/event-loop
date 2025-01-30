import enum
from typing import NamedTuple, TypeAlias


class TimeCondition(NamedTuple):
    when: float


class IOConditionKind(enum.Enum):
    READ = 'read'
    WRITE = 'write'


class IOCondition(NamedTuple):
    fd: int
    kind: IOConditionKind


Condition: TypeAlias = TimeCondition | IOCondition
