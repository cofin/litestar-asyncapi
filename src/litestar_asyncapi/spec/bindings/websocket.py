from dataclasses import dataclass
from typing import Any

from litestar_asyncapi.spec.bindings.base import Binding

__all__ = ("WebSocketChannelBinding", "WebSocketMessageBinding", "WebSocketServerBinding")


@dataclass(slots=True)
class WebSocketServerBinding(Binding):
    """WebSocket server binding, which defines no protocol-specific fields."""


@dataclass(slots=True)
class WebSocketChannelBinding(Binding):
    """WebSocket channel binding describing the opening handshake."""

    method: str | None = None
    """HTTP method of the opening handshake: ``GET`` or ``POST``."""
    query: dict[str, Any] | None = None
    """Schema of the query parameters of the opening handshake."""
    headers: dict[str, Any] | None = None
    """Schema of the HTTP headers of the opening handshake."""


@dataclass(slots=True)
class WebSocketMessageBinding(Binding):
    """WebSocket message binding, which defines no protocol-specific fields."""
