import pytest

from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator

pytestmark = pytest.mark.anyio


def test_generator_populates_components_schemas_for_attrs_payloads() -> None:
    attrs = pytest.importorskip("attrs")
    from litestar import Litestar, websocket_listener

    @attrs.define
    class Payload:
        value: int

    @websocket_listener("/listen", signature_namespace={"Payload": Payload})
    async def listener(socket: object, data: Payload) -> Payload:
        raise RuntimeError

    app = Litestar(route_handlers=[listener])
    from litestar_asyncapi import AsyncAPIConfig

    document = AsyncAPIGenerator(app=app, config=AsyncAPIConfig()).build_asyncapi()
    assert document.components.schemas
    assert any(k.endswith("Payload") for k in document.components.schemas)


def test_explicit_components_and_literal_references_are_preserved() -> None:
    from litestar import Litestar

    from litestar_asyncapi import AsyncAPIConfig, ChannelDefinition, MessageDefinition, OperationDefinition
    from litestar_asyncapi.spec import (
        Components,
        CorrelationId,
        MessageTrait,
        OperationTrait,
        Reference,
        Reply,
        Schema,
        SecurityScheme,
        Server,
    )

    components = Components(
        schemas={"Shared": Schema(type="integer")},
        security_schemes={"auth": SecurityScheme(type="userPassword")},
        correlation_ids={"id": CorrelationId(location="$message.header#/id")},
        operation_traits={"common": OperationTrait(summary="shared")},
        message_traits={"shared": MessageTrait(summary="message")},
        replies={
            "reply": Reply(
                channel=Reference(ref="#/channels/response"),
                messages=[Reference(ref="#/channels/response/messages/result")],
            )
        },
    )
    config = AsyncAPIConfig(
        components=components,
        servers={"main": Server(host="localhost", protocol="ws")},
        channels=[
            ChannelDefinition(
                "request",
                "/request",
                servers=[Reference(ref="#/servers/main")],
                operations=[
                    OperationDefinition(
                        action="receive",
                        operation_id="request",
                        security=[Reference(ref="#/components/securitySchemes/auth")],
                        traits=["common"],
                        reply=Reference(ref="#/components/replies/reply"),
                        messages=[
                            MessageDefinition(
                                name="input",
                                payload={"$ref": "#/components/schemas/Shared"},
                                correlation_id=Reference(ref="#/components/correlationIds/id"),
                                traits=["shared"],
                                examples=[{"$ref": "https://literal.invalid/value"}],
                            )
                        ],
                    )
                ],
            ),
            ChannelDefinition(
                "response",
                "/response",
                operations=[
                    OperationDefinition(action="send", messages=[MessageDefinition(name="result", payload=int)])
                ],
            ),
        ],
    )
    document = AsyncAPIGenerator(Litestar([]), config).build_schema()
    assert document["components"]["securitySchemes"]["auth"] == {"type": "userPassword"}
    assert document["channels"]["request"]["messages"]["input"]["examples"] == [
        {"payload": {"$ref": "https://literal.invalid/value"}}
    ]
    assert components.schemas == {"Shared": Schema(type="integer")}


@pytest.mark.parametrize("reference", ["#/components/messageTraits/missing", "#/components/schemas/exists"])
def test_trait_reference_requires_existing_correct_target(reference: str) -> None:
    from litestar import Litestar
    from litestar.exceptions import ImproperlyConfiguredException

    from litestar_asyncapi import AsyncAPIConfig, ChannelDefinition, MessageDefinition, OperationDefinition
    from litestar_asyncapi.spec import Components, Reference, Schema

    config = AsyncAPIConfig(
        components=Components(schemas={"exists": Schema(type="string")}),
        channels=[
            ChannelDefinition(
                "events",
                "events",
                [
                    OperationDefinition(
                        action="send", messages=[MessageDefinition(payload=str, traits=[Reference(ref=reference)])]
                    )
                ],
            )
        ],
    )
    with pytest.raises(ImproperlyConfiguredException, match="messageTrait reference"):
        AsyncAPIGenerator(Litestar([]), config).build_schema()


def test_local_payload_reference_can_target_another_channel_schema() -> None:
    from litestar import Litestar

    from litestar_asyncapi import AsyncAPIConfig, ChannelDefinition, MessageDefinition, OperationDefinition

    config = AsyncAPIConfig(
        channels=[
            ChannelDefinition(
                "x",
                "x",
                [
                    OperationDefinition(
                        action="send", messages=[MessageDefinition(name="m", payload={"type": "integer"})]
                    )
                ],
            ),
            ChannelDefinition(
                "y",
                "y",
                [
                    OperationDefinition(
                        action="send",
                        messages=[MessageDefinition(name="m", payload={"$ref": "#/channels/x/messages/m/payload"})],
                    )
                ],
            ),
        ]
    )
    assert AsyncAPIGenerator(Litestar([]), config).build_schema()["channels"]["y"]["messages"]["m"]["payload"] == {
        "$ref": "#/channels/x/messages/m/payload"
    }


def test_aliased_channels_and_reply_message_membership() -> None:
    from litestar.exceptions import ImproperlyConfiguredException

    from litestar_asyncapi.asyncapi.generator import _validate_references

    document = {
        "channels": {"root": {"$ref": "#/components/channels/shared"}},
        "components": {"channels": {"shared": {"messages": {"m": {"payload": {"type": "integer"}}}}}},
        "operations": {
            "send": {
                "channel": {"$ref": "#/channels/root"},
                "messages": [{"$ref": "#/components/channels/shared/messages/m"}],
                "reply": {
                    "channel": {"$ref": "#/channels/root"},
                    "messages": [{"$ref": "#/components/channels/shared/messages/m"}],
                },
            }
        },
    }
    _validate_references(document)
    document["components"]["messages"] = {"other": {"payload": {"type": "string"}}}
    document["operations"]["send"]["reply"]["messages"] = [{"$ref": "#/components/messages/other"}]
    with pytest.raises(ImproperlyConfiguredException, match="does not belong"):
        _validate_references(document)


def test_component_collision_reports_both_sources() -> None:
    from litestar import Litestar
    from litestar.exceptions import ImproperlyConfiguredException

    from litestar_asyncapi import AsyncAPIConfig
    from litestar_asyncapi.spec import Components, MessageTrait

    config = AsyncAPIConfig(
        components=Components(message_traits={"same": MessageTrait(summary="first")}),
        message_traits={"same": MessageTrait(summary="second")},
    )
    with pytest.raises(
        ImproperlyConfiguredException, match=r"messageTraits/same.*AsyncAPIConfig.components.*configured"
    ):
        AsyncAPIGenerator(Litestar([]), config).build_schema()


def test_channel_server_reference_must_select_root_and_external_is_preserved() -> None:
    from litestar import Litestar
    from litestar.exceptions import ImproperlyConfiguredException

    from litestar_asyncapi import AsyncAPIConfig, ChannelDefinition
    from litestar_asyncapi.spec import Components, Reference, Server

    config = AsyncAPIConfig(
        components=Components(servers={"shared": Server(host="localhost", protocol="ws")}),
        channels=[ChannelDefinition("c", "c", servers=[Reference(ref="#/components/servers/shared")])],
    )
    with pytest.raises(ImproperlyConfiguredException, match="must select a root server"):
        AsyncAPIGenerator(Litestar([]), config).build_schema()
    config.channels[0].servers = [Reference(ref="https://unfetched.invalid/server.json")]
    assert AsyncAPIGenerator(Litestar([]), config).build_schema()["channels"]["c"]["servers"] == [
        {"$ref": "https://unfetched.invalid/server.json"}
    ]


def test_explicit_component_cannot_overwrite_native_generated_schema() -> None:
    from dataclasses import dataclass

    from litestar import Litestar
    from litestar.exceptions import ImproperlyConfiguredException

    from litestar_asyncapi import AsyncAPIConfig, ChannelDefinition, MessageDefinition, OperationDefinition
    from litestar_asyncapi.spec import Components, Schema

    @dataclass
    class Payload:
        value: int

    config = AsyncAPIConfig(
        channels=[
            ChannelDefinition(
                "c", "c", [OperationDefinition(action="send", messages=[MessageDefinition(payload=Payload)])]
            )
        ]
    )
    app = Litestar([])
    key = next(iter(AsyncAPIGenerator(app, config).build_schema()["components"]["schemas"]))
    config.components = Components(schemas={key: Schema(type="string")})
    with pytest.raises(ImproperlyConfiguredException, match="Conflicting component schemas"):
        AsyncAPIGenerator(app, config).build_schema()
