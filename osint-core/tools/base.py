from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from enum import Enum


class ToolStatus(Enum):
    READY = "ready"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"


class OSINTResult:
    def __init__(
        self,
        tool_name: str,
        query: str,
        status: ToolStatus,
        data: Any = None,
        confidence: float = 0.0,
        source_url: str = "",
        error_message: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.tool_name = tool_name
        self.query = query
        self.status = status
        self.data = data
        self.confidence = confidence
        self.source_url = source_url
        self.error_message = error_message
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "query": self.query,
            "status": self.status.value,
            "data": self.data,
            "confidence": self.confidence,
            "source_url": self.source_url,
            "error_message": self.error_message,
            "metadata": self.metadata,
        }


class OSINTTool(ABC):
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    def category(self) -> str:
        pass

    @abstractmethod
    def input_schema(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> OSINTResult:
        pass

    @abstractmethod
    def confidence_score(self, result: OSINTResult) -> float:
        pass

    def is_stealth(self) -> bool:
        return False

    def requires_api_key(self) -> bool:
        return False

    def is_free(self) -> bool:
        return True

    def get_api_key_name(self) -> str:
        return self.name()

    def get_cost_info(self) -> Dict[str, Any]:
        return {
            "is_free": self.is_free(),
            "requires_api_key": self.requires_api_key(),
            "note": "No cost",
        }

    def validate_params(self, params: Dict[str, Any]) -> tuple[bool, str]:
        schema = self.input_schema()
        for field, spec in schema.get("required", {}).items():
            if field not in params or params[field] is None:
                return False, f"Missing required parameter: {field}"
        return True, ""