from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest
from litestar import Litestar, websocket_listener

from litestar_asyncapi import AsyncAPIConfig, asyncapi_message
from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator

if TYPE_CHECKING:
    from litestar import WebSocket

pytestmark = pytest.mark.anyio


def test_decorator_examples_override_generated_examples() -> None:
    @dataclass
    class Payload:
        value: int

    @asyncapi_message(action="receive", payload=Payload, examples=[{"value": 123}])
    @websocket_listener("/ws", signature_namespace={"Payload": Payload})
    async def handler(socket: "WebSocket", data: Payload) -> Payload:
        raise RuntimeError

    app = Litestar(route_handlers=[handler])
    config = AsyncAPIConfig(create_examples=True)
    document = AsyncAPIGenerator(app, config).build_schema()
    messages = document["channels"]["/ws"]["messages"]
    receive = next(message for key, message in messages.items() if "receive" in key)
    send = next(message for key, message in messages.items() if "send" in key)
    assert receive["examples"] == [{"payload": {"value": 123}}]
    assert isinstance(send["examples"][0]["payload"]["value"], int)


def test_explicit_empty_examples_prevent_generation(monkeypatch) -> None:
    def unexpected(*args, **kwargs):
        pytest.fail("Explicit examples must prevent automatic generation")

    monkeypatch.setattr("litestar_asyncapi.asyncapi.utils.examples.native_example_value", unexpected)

    @asyncapi_message(action="receive", examples=[])
    @websocket_listener("/empty")
    async def handler(data: int) -> None:
        return None

    app = Litestar([handler])
    document = AsyncAPIGenerator(app, AsyncAPIConfig(create_examples=True)).build_schema()
    assert next(iter(document["channels"]["/empty"]["messages"].values()))["examples"] == []


def test_declared_model_examples_precede_generation(monkeypatch) -> None:
    from pydantic import BaseModel, ConfigDict

    class Payload(BaseModel):
        model_config = ConfigDict(json_schema_extra={"examples": [{"value": None}]})
        value: int | None

    def unexpected(*args, **kwargs):
        pytest.fail("Declared examples must prevent automatic generation")

    monkeypatch.setattr("litestar_asyncapi.asyncapi.utils.examples.native_example_value", unexpected)

    @websocket_listener("/declared", signature_namespace={"Payload": Payload})
    async def handler(data: Payload) -> None:
        return None

    app = Litestar([handler])
    document = AsyncAPIGenerator(app, AsyncAPIConfig(create_examples=True)).build_schema()
    assert next(iter(document["channels"]["/declared"]["messages"].values()))["examples"] == [
        {"payload": {"value": None}}
    ]


def test_explicit_null_message_example_is_preserved() -> None:
    @asyncapi_message(action="receive", examples=[None])
    @websocket_listener("/null")
    async def handler(data: int | None) -> None:
        return None

    app = Litestar([handler])
    document = AsyncAPIGenerator(app, AsyncAPIConfig()).build_schema()
    assert next(iter(document["channels"]["/null"]["messages"].values()))["examples"] == [{"payload": None}]


@pytest.mark.parametrize("enabled", [False, True])
def test_explicit_multiformat_payload_does_not_generate_examples(enabled: bool) -> None:
    from litestar_asyncapi.spec import MultiFormatSchema

    @asyncapi_message(
        action="receive", payload=MultiFormatSchema("application/schema+json;version=draft-07", {"type": "string"})
    )
    @websocket_listener("/explicit-schema")
    async def handler(data: str) -> None:
        return None

    app = Litestar([handler])
    document = AsyncAPIGenerator(app, AsyncAPIConfig(create_examples=enabled)).build_schema()
    assert "examples" not in next(iter(document["channels"]["/explicit-schema"]["messages"].values()))
