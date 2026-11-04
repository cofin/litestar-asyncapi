import inspect
from typing import Any

from litestar_asyncapi._compat import websocket_handler_callback

__all__ = ("get_handler_docstring",)


def get_handler_docstring(route_handler: Any) -> str | None:
    """Return the normalized docstring of the user callback behind a WebSocket route handler.

    Args:
        route_handler: A Litestar WebSocket route handler.

    Returns:
        The normalized docstring, or ``None`` if the callback has none.
    """
    docstring = inspect.getdoc(websocket_handler_callback(route_handler))
    return docstring.strip() or None if docstring else None
