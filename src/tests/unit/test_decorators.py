from typing import Any

import pytest
from litestar import websocket_listener

from litestar_asyncapi.decorators import ASYNCAPI_OPT_KEY, AsyncAPIMetadata, asyncapi_message, asyncapi_operation
from litestar_asyncapi.spec import OperationAction

pytestmark = pytest.mark.anyio


def test_decorators_attach_metadata_to_handler_opt() -> None:
    def fn(socket: Any, data: Any) -> Any:
        return None

    handler = websocket_listener("/ws")(fn)
    asyncapi_operation(action="receive", operation_id="recv", summary="in")(handler)
    asyncapi_message(action=OperationAction.RECEIVE, payload=int, name="Inbound")(handler)

    assert ASYNCAPI_OPT_KEY in handler.opt
    metadata = handler.opt[ASYNCAPI_OPT_KEY]
    assert isinstance(metadata, AsyncAPIMetadata)
    operation = metadata.operations[OperationAction.RECEIVE]
    assert operation.operation_id == "recv"
    assert operation.summary == "in"
    assert operation.message is not None
    assert operation.message.name == "Inbound"
    assert operation.message.payload is int
