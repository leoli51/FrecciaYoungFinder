from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Station:
    display_name: str
    id: int
    name: str

    @classmethod
    def from_api_response(cls, api_response: dict[str, Any]) -> Station:
        return cls(
            display_name=api_response["displayName"],
            id=api_response["id"],
            name=api_response["name"],
        )
