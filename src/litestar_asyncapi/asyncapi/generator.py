import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from litestar.exceptions import ImproperlyConfiguredException

from litestar_asyncapi.asyncapi.extractors import extract_channels_plugin_channels, extract_websocket_channels
from litestar_asyncapi.asyncapi.schema_generation import AsyncAPISchemaGenerator
from litestar_asyncapi.spec import AsyncAPI, Channel, Components, Info, Message, Operation, OperationAction, Reference

if TYPE_CHECKING:
    from litestar import Litestar

    from litestar_asyncapi import AsyncAPIConfig
    from litestar_asyncapi.spec import MessageTrait, OperationTrait, Schema

__all__ = ("AsyncAPIGenerator",)


INVALID_OPERATION_ID_CHARS = re.compile(r"[^a-zA-Z0-9_.-]+")


@dataclass(slots=True)
class AsyncAPIGenerator:
    """Build AsyncAPI documents from Litestar apps and AsyncAPIConfig."""

    app: "Litestar"
    config: "AsyncAPIConfig"

    def build_asyncapi(self) -> AsyncAPI:
        """Build an AsyncAPI document object.

        Returns:
            The generated AsyncAPI document.
        """
        schema_generator = AsyncAPISchemaGenerator()
        info = Info(title=self.config.title, version=self.config.version, description=self.config.description)
        document = AsyncAPI(info=info, default_content_type=self.config.default_content_type)

        document.servers = self.config.to_servers()

        discovered = _discover_channels(self.app, self.config, schema_generator)
        _populate_channels(document, discovered)
        _populate_operations(document, discovered, config=self.config)

        schemas = schema_generator.schema_registry.generate_components_schemas()
        component_schemas: "dict[str, Schema | Reference]" = dict(schemas)
        document.components = Components(
            schemas=component_schemas,
            operation_traits=self.config.to_operation_traits(),
            message_traits=self.config.to_message_traits(),
        )

        return document

    def build_schema(self) -> dict[str, Any]:
        """Build a serialized AsyncAPI document dict.

        Returns:
            The generated AsyncAPI document as a ``dict``.
        """
        return self.build_asyncapi().to_schema()


def _default_operation_id(channel_key: str, action: OperationAction) -> str:
    return f"{channel_key}_{action.value}"


def _channel_key(address: str) -> str:
    # For now use the address as the key. This matches common AsyncAPI usage where channel keys are the address.
    # References must escape according to JSON pointer rules.
    return address


def _json_pointer_escape(segment: str) -> str:
    return segment.replace("~", "~0").replace("/", "~1")


def _sanitize_operation_id(value: str) -> str:
    return re.sub(INVALID_OPERATION_ID_CHARS, "_", value).strip("_")


def _ensure_unique_operation_id(
    operation_id: str,
    *,
    default_operation_id: str,
    used_ids: set[str],
    used_keys: set[str],
) -> tuple[str, str]:
    base_id = operation_id or default_operation_id
    candidate = base_id
    suffix = 1

    while True:
        key = _sanitize_operation_id(candidate) or _sanitize_operation_id(default_operation_id)
        if key and candidate not in used_ids and key not in used_keys:
            return candidate, key
        suffix += 1
        candidate = f"{base_id}_{suffix}"


def _ensure_unique_message_key(message_key: str, used_keys: set[str]) -> str:
    candidate = message_key
    suffix = 1
    while candidate in used_keys:
        suffix += 1
        candidate = f"{message_key}_{suffix}"
    used_keys.add(candidate)
    return candidate


def _discover_channels(
    app: "Litestar", config: "AsyncAPIConfig", schema_generator: AsyncAPISchemaGenerator
) -> list[Any]:
    discovered: list[Any] = []
    if config.include_websocket_routes:
        discovered.extend(extract_websocket_channels(app, schema_generator=schema_generator, config=config))
    if config.include_channels_plugin:
        discovered.extend(extract_channels_plugin_channels(app, schema_generator=schema_generator))
    return discovered


def _populate_channels(document: AsyncAPI, discovered: list[Any]) -> None:
    for discovered_channel in discovered:
        channel_key = _channel_key(discovered_channel.address)
        document.channels[channel_key] = Channel(
            address=discovered_channel.address,
            parameters=discovered_channel.parameters,
        )


def _populate_operations(document: AsyncAPI, discovered: list[Any], *, config: "AsyncAPIConfig") -> None:
    used_operation_ids: set[str] = set()
    used_operation_keys: set[str] = set()
    channel_message_keys: dict[str, set[str]] = {}

    for discovered_channel in discovered:
        channel_key = _channel_key(discovered_channel.address)
        channel_ref = Reference(ref=f"#/channels/{_json_pointer_escape(channel_key)}")
        channel = document.channels[channel_key]
        for discovered_operation in discovered_channel.operations:
            default_operation_id = _default_operation_id(channel_key, discovered_operation.action)
            operation_id, operation_key = _ensure_unique_operation_id(
                discovered_operation.operation_id or default_operation_id,
                default_operation_id=default_operation_id,
                used_ids=used_operation_ids,
                used_keys=used_operation_keys,
            )
            used_operation_ids.add(operation_id)
            used_operation_keys.add(operation_key)

            messages: list[Message | Reference] | None = None
            if discovered_operation.message is not None:
                message = discovered_operation.message.to_spec_message()
                if discovered_operation.message.traits:
                    message.traits = _resolve_message_traits(
                        discovered_operation.message.traits,
                        config=config,
                    )
                message_key = _ensure_unique_message_key(
                    operation_key,
                    channel_message_keys.setdefault(channel_key, set()),
                )
                channel.messages = channel.messages or {}
                channel.messages[message_key] = message
                messages = [
                    Reference(
                        ref=f"#/channels/{_json_pointer_escape(channel_key)}/messages/{_json_pointer_escape(message_key)}"
                    )
                ]

            operation_trait_refs = (
                _resolve_operation_traits(discovered_operation.traits, config=config)
                if discovered_operation.traits
                else None
            )

            document.operations[operation_key] = Operation(
                action=discovered_operation.action,
                channel=channel_ref,
                operation_id=operation_id,
                title=discovered_operation.title,
                summary=discovered_operation.summary,
                description=discovered_operation.description,
                messages=messages,
                traits=operation_trait_refs,
            )


def _resolve_operation_traits(traits: list[str], *, config: "AsyncAPIConfig") -> "list[OperationTrait | Reference]":
    available = config.to_operation_traits()
    missing = [name for name in traits if name not in available]
    if missing:
        msg = f"Unknown operation traits referenced: {missing!r}. Register them on AsyncAPIConfig.operation_traits."
        raise ImproperlyConfiguredException(msg)
    return [Reference(ref=f"#/components/operationTraits/{_json_pointer_escape(name)}") for name in traits]


def _resolve_message_traits(traits: list[str], *, config: "AsyncAPIConfig") -> "list[MessageTrait | Reference]":
    available = config.to_message_traits()
    missing = [name for name in traits if name not in available]
    if missing:
        msg = f"Unknown message traits referenced: {missing!r}. Register them on AsyncAPIConfig.message_traits."
        raise ImproperlyConfiguredException(msg)
    return [Reference(ref=f"#/components/messageTraits/{_json_pointer_escape(name)}") for name in traits]
