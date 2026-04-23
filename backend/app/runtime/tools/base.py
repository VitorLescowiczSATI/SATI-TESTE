from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, ClassVar, Generic, TypeVar

from pydantic import BaseModel

PayloadT = TypeVar("PayloadT", bound=BaseModel)


@dataclass(slots=True)
class ToolExecutionResult:
    message_to_agent: str
    state_updates: dict[str, Any] = field(default_factory=dict)
    tags_to_add: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class RuntimeTool(ABC, Generic[PayloadT]):
    name: ClassVar[str]
    description: ClassVar[str]
    payload_model: ClassVar[type[PayloadT]]

    @classmethod
    def json_schema(cls) -> dict[str, Any]:
        return cls.payload_model.model_json_schema()

    @classmethod
    def parse_payload(cls, data: dict[str, Any]) -> PayloadT:
        return cls.payload_model.model_validate(data)

    @abstractmethod
    def execute(self, payload: PayloadT) -> ToolExecutionResult:
        raise NotImplementedError
