from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ModuleResult:
    found: bool
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    cached: bool = False


class BaseModule(ABC):
    name: str
    accepted_target_types: list[str]
    requires_api_key: bool = False

    @abstractmethod
    def run(self, target_value: str, api_key: str | None = None) -> ModuleResult:
        """Execute the module against the given target value."""
        ...

    def accepts(self, target_type: str) -> bool:
        return target_type in self.accepted_target_types
