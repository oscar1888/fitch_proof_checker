from dataclasses import dataclass
from typing import ClassVar


@dataclass
class Rule:
    name: ClassVar[str]
