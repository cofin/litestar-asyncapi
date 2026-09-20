# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "litestar[standard]",
#     "litestar-asyncapi",
# ]
# [tool.uv.sources]
# litestar-asyncapi = { path = "../../.." }
# ///
"""Error handling example demonstrating WebSocket error scenarios.

This example shows how WebSocket handlers can gracefully handle various
error conditions and how the AsyncAPI documentation reflects the message schemas.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from litestar import Litestar, websocket_listener
from litestar.dto import DataclassDTO

from litestar_asyncapi import AsyncAPIConfig, AsyncAPIPlugin, DocsConfig
from litestar_asyncapi.spec import Server

if TYPE_CHECKING:
    from litestar import WebSocket

__all__ = ("ErrorPayload", "ErrorResponse", "error_demo")


@dataclass
class ErrorPayload:
    """Payload for triggering error scenarios."""

    action: str
    """Action to perform: 'echo', 'error', or 'validate'."""
    value: str | None = None
    """Optional value for the action."""


@dataclass
class ErrorResponse:
    """Response from the error demo handler."""

    status: str
    """Status of the operation: 'ok' or 'error'."""
    message: str
    """Descriptive message about the result."""
    original_action: str | None = None
    """The action that was requested."""


_INTENTIONAL_ERROR_MSG = "Intentional error triggered by client"


@websocket_listener(
    "/ws/errors",
    dto=DataclassDTO[ErrorPayload],
    return_dto=DataclassDTO[ErrorResponse],
    signature_namespace={"ErrorPayload": ErrorPayload, "ErrorResponse": ErrorResponse},
)
async def error_demo(socket: "WebSocket", data: ErrorPayload) -> ErrorResponse:
    """Handle messages and demonstrate error scenarios.

    Supported actions:
    - 'echo': Echo back the value
    - 'error': Intentionally raise an error
    - 'validate': Validate the value is not empty

    Args:
        socket: The WebSocket connection.
        data: The incoming payload with action and optional value.

    Returns:
        ErrorResponse with status and message.

    Raises:
        ValueError: When action is 'error' to demonstrate error handling.
    """
    if data.action == "echo":
        return ErrorResponse(status="ok", message=f"Echoed: {data.value}", original_action=data.action)
    if data.action == "error":
        raise ValueError(_INTENTIONAL_ERROR_MSG)
    if data.action == "validate":
        if not data.value:
            return ErrorResponse(
                status="error", message="Validation failed: value is required", original_action=data.action
            )
        return ErrorResponse(status="ok", message=f"Validation passed for: {data.value}", original_action=data.action)
    return ErrorResponse(status="error", message=f"Unknown action: {data.action}", original_action=data.action)


config = AsyncAPIConfig(
    title="Error Handling",
    docs=DocsConfig(interactive=True),
    servers={"local": Server(host="localhost:8000", protocol="ws")},
)

app = Litestar(route_handlers=[error_demo], plugins=[AsyncAPIPlugin(config)])
