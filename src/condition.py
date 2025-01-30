import enum
from typing import NamedTuple


class TimeCondition(NamedTuple):
    when: float


class IOConditionKind(enum.Enum):
    READ = 'read'
    WRITE = 'write'


class IOCondition(NamedTuple):
    fd: int
    kind: IOConditionKind


type Condition = TimeCondition | IOCondition
