from litestar import websocket, websocket_listener

from litestar_asyncapi.asyncapi.utils.docstrings import get_handler_docstring


def test_get_handler_docstring_reads_the_unwrapped_listener_callback() -> None:
    @websocket_listener("/ws")
    async def handler(data: str) -> None:
        """Summary line.

        Additional details.
        """

    assert get_handler_docstring(handler) == "Summary line.\n\nAdditional details."


def test_get_handler_docstring_returns_none_when_missing() -> None:
    @websocket("/raw")
    async def handler(socket: object) -> None:
        return None

    assert get_handler_docstring(handler) is None
