from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, ClassVar

from app.runtime.tools import RuntimeTool


@dataclass(frozen=True, slots=True)
class StrategyRuntimeConfig:
    key: str
    display_name: str
    model: str
    max_tokens: int
    idle_timeout_minutes: int
    input_debounce_seconds: int
    image_mode: str = "wait"


class BaseStrategy(ABC):
    config: ClassVar[StrategyRuntimeConfig]
    tools: ClassVar[tuple[type[RuntimeTool[Any]], ...]] = ()

    @classmethod
    def tool_registry(cls) -> dict[str, RuntimeTool[Any]]:
        return {tool_cls.name: tool_cls() for tool_cls in cls.tools}

    @classmethod
    def tool_schemas(cls) -> dict[str, dict[str, Any]]:
        return {tool_cls.name: tool_cls.json_schema() for tool_cls in cls.tools}

    @classmethod
    @abstractmethod
    def build_system_prompt(cls, current_moment: str) -> str:
        raise NotImplementedError
