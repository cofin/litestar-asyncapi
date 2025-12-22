from dataclasses import dataclass
from typing import Any

from litestar_asyncapi.spec.bindings.base import Binding

__all__ = (
    "WebSocketChannelBinding",
    "WebSocketMessageBinding",
    "WebSocketServerBinding",
)


@dataclass(slots=True)
class WebSocketServerBinding(Binding):
    """WebSocket server binding (minimal initial model)."""

    method: str | None = None
    query: dict[str, Any] | None = None
    headers: dict[str, Any] | None = None


@dataclass(slots=True)
class WebSocketChannelBinding(Binding):
    """WebSocket channel binding (minimal initial model)."""

    method: str | None = None
    query: dict[str, Any] | None = None
    headers: dict[str, Any] | None = None


@dataclass(slots=True)
class WebSocketMessageBinding(Binding):
    """WebSocket message binding (minimal initial model)."""

    headers: dict[str, Any] | None = None
