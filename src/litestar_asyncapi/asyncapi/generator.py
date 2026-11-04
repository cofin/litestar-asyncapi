import json
import re
import warnings
from copy import deepcopy
from dataclasses import dataclass, fields, is_dataclass, replace
from typing import TYPE_CHECKING, Any, NoReturn, TypeVar, cast
from urllib.parse import quote, unquote

from litestar.exceptions import ImproperlyConfiguredException
from litestar.typing import FieldDefinition

from litestar_asyncapi._compat import NativeDTOPayload, resolve_annotation
from litestar_asyncapi.asyncapi.datastructures import (
    SOURCE_EXTENSION,
    SOURCE_MARKERS,
    ChannelDefinition,
    DiscoveredChannel,
    DiscoveredOperation,
    DiscoverySource,
    MessageDefinition,
    OperationDefinition,
    ReplyDefinition,
)
from litestar_asyncapi.asyncapi.extractors import (
    extract_channels_plugin_channels,
    extract_sse_channels,
    extract_websocket_channels,
)
from litestar_asyncapi.asyncapi.openapi import (
    OPENAPI_SERVERS_SOURCE,
    OPENAPI_SOURCE,
    inherited_info,
    inherited_security_schemes,
    inherited_servers,
)
from litestar_asyncapi.asyncapi.schema_generation import AsyncAPISchemaGenerator
from litestar_asyncapi.asyncapi.utils.examples import generate_example, normalize_examples
from litestar_asyncapi.spec import (
    AsyncAPI,
    Channel,
    Message,
    MessageTrait,
    MultiFormatSchema,
    Operation,
    OperationAction,
    OperationTrait,
    Reference,
    Reply,
    Schema,
)
from litestar_asyncapi.spec.base import UNSET, BaseSchemaObject

if TYPE_CHECKING:
    from collections.abc import Sequence

    from litestar import Litestar

    from litestar_asyncapi import AsyncAPIConfig

__all__ = ("AsyncAPIGenerator",)


INVALID_OPERATION_ID_CHARS = re.compile(r"[^a-zA-Z0-9_.-]+")

T = TypeVar("T")


@dataclass(slots=True)
class AsyncAPIGenerator:
    """Build AsyncAPI documents from Litestar apps and AsyncAPIConfig."""

    app: "Litestar"
    """Application whose routes and plugins are documented."""
    config: "AsyncAPIConfig"
    """Configuration that supplies metadata, explicit contracts and discovery flags."""

    def build_asyncapi(self) -> AsyncAPI:
        """Build an AsyncAPI document object.

        Returns:
            The generated AsyncAPI document.
        """
        schema_generator = AsyncAPISchemaGenerator(self.app)
        openapi = self.app.openapi_config
        document = AsyncAPI(
            info=inherited_info(self.config, openapi),
            asyncapi=self.config.spec_version,
            default_content_type=self.config.default_content_type,
        )

        document.servers.update(self.config.to_servers())
        derived_servers = (
            inherited_servers(openapi) if self.config.inherit_openapi and self.config.inherit_openapi_servers else {}
        )
        for name, server in derived_servers.items():
            if name in document.servers and _definition_key(document.servers[name]) != _definition_key(server):
                message = f"Conflicting server {name!r}: AsyncAPIConfig.servers and {OPENAPI_SERVERS_SOURCE}"
                raise ImproperlyConfiguredException(message)
            document.servers[name] = server

        document.components = deepcopy(self.config.components)
        if self.config.inherit_openapi:
            _merge_components(
                document.components.security_schemes,
                inherited_security_schemes(openapi),
                "securitySchemes",
                source=OPENAPI_SOURCE,
            )
        _merge_components(document.components.operation_traits, self.config.to_operation_traits(), "operationTraits")
        _merge_components(document.components.message_traits, self.config.to_message_traits(), "messageTraits")
        discovered = _normalize_channels(_discover_channels(self.app, self.config, schema_generator))
        channels = _populate_channels(document, discovered, websocket_servers=list(derived_servers))
        _populate_operations(
            document, discovered, channels, config=self.config, schema_generator=schema_generator, app=self.app
        )

        _merge_components(document.components.schemas, schema_generator.components(), "schemas")
        _validate_references(document.to_schema())

        return document

    def build_schema(self) -> dict[str, Any]:
        """Build a serialized AsyncAPI document dict.

        Returns:
            The generated AsyncAPI document as a ``dict``.
        """
        return self.build_asyncapi().to_schema()


def _default_operation_id(channel_key: str, action: OperationAction) -> str:
    return f"{channel_key}_{action.value}"


def _json_pointer_escape(segment: str) -> str:
    return quote(segment.replace("~", "~0").replace("/", "~1"), safe="~")


def _sanitize_operation_id(value: str) -> str:
    return re.sub(INVALID_OPERATION_ID_CHARS, "_", value).strip("_")


def _ensure_unique_operation_id(
    operation_id: str, *, default_operation_id: str, used_ids: set[str], used_keys: set[str], config: "AsyncAPIConfig"
) -> tuple[str, str]:
    """Ensure operation identity and mapping keys are unique across the document.

    Uses case-insensitive checks for IDs and keys to satisfy strict tooling requirements.
    """
    base_id = operation_id or default_operation_id
    candidate = base_id
    base_key = _sanitize_operation_id(base_id) or _sanitize_operation_id(default_operation_id)
    suffix = 1

    while True:
        key = base_key if suffix == 1 else f"{base_key}_{suffix}"
        candidate_fold = candidate.casefold()
        key_fold = key.casefold()

        is_id_used = candidate_fold in used_ids
        is_key_used = key_fold in used_keys

        if not (is_id_used or is_key_used):
            return candidate, key

        if config.strict_uniqueness:
            msg = f"Duplicate operationId found: {candidate!r} (key: {key!r}). Disable 'strict_uniqueness' to allow automatic suffixing."
            raise ImproperlyConfiguredException(msg)

        suffix += 1
        candidate = f"{base_id}_{suffix}"


def _ensure_unique_message_key(message_key: str, used_keys: set[str]) -> str:
    candidate = message_key
    suffix = 1
    while candidate.casefold() in used_keys:
        suffix += 1
        candidate = f"{message_key}_{suffix}"
    used_keys.add(candidate.casefold())
    return candidate


def _discover_channels(
    app: "Litestar", config: "AsyncAPIConfig", schema_generator: AsyncAPISchemaGenerator
) -> list[DiscoveredChannel]:
    discovered: list[DiscoveredChannel] = []
    if config.include_websocket_routes:
        discovered.extend(extract_websocket_channels(app, schema_generator=schema_generator, config=config))
    discovered.extend(extract_channels_plugin_channels(app, schema_generator=schema_generator, config=config))
    discovered.extend(extract_sse_channels(app, schema_generator=schema_generator, config=config))
    explicit: dict[str, tuple[ChannelDefinition, str]] = {}
    for index, channel in enumerate(config.channels):
        source = f"AsyncAPIConfig.channels[{index}] ({channel.key})"
        if channel.key in explicit:
            message = f"Conflicting explicit channel {channel.key!r}: {explicit[channel.key][1]} and {source}"
            raise ImproperlyConfiguredException(message)
        explicit[channel.key] = (channel, source)
    for channel in discovered:
        if (
            channel.key in explicit
            and channel.source is DiscoverySource.CHANNELS_PLUGIN
            and channel.route_identity is None
        ):
            message = (
                f"Conflicting channel {channel.key!r}: {channel.provenance} and {explicit[channel.key][1]}; "
                "type the topic with AsyncAPIConfig.channel_payloads or set include_channels_plugin_topics=False"
            )
            raise ImproperlyConfiguredException(message)
    discovered = [channel for channel in discovered if channel.key not in explicit]
    discovered.extend(
        DiscoveredChannel(
            **{
                item.name: getattr(channel, item.name)
                for item in fields(ChannelDefinition)
                if item.name != "operations"
            },
            operations=[
                DiscoveredOperation(
                    **{item.name: getattr(operation, item.name) for item in fields(OperationDefinition)},
                    provenance=f"{source}.operations[{index}]",
                )
                for index, operation in enumerate(channel.operations)
            ],
            source=DiscoverySource.CONFIG,
            provenance=source,
            route_identity=None,
        )
        for channel, source in explicit.values()
    )
    return discovered


def _populate_channels(
    document: AsyncAPI, discovered: list[DiscoveredChannel], *, websocket_servers: list[str]
) -> dict[str, Channel]:
    """Add one inline channel per discovered channel and return them by key.

    Discovered channels carry an ``x-litestar-source`` transport marker unless their own extensions set one.
    WebSocket channels without explicit servers are bound to ``websocket_servers``.
    """
    channels = {
        channel.key: Channel(
            address=channel.address,
            description=channel.description,
            parameters=channel.parameters,
            servers=_resolve_names(
                websocket_servers
                if channel.servers is None and channel.source is DiscoverySource.WEBSOCKET and websocket_servers
                else channel.servers,
                available=document.servers,
                kind="server",
                pointer="#/servers",
                context=f" in {channel.provenance}",
            ),
            bindings=channel.bindings,
            extensions=(
                {SOURCE_EXTENSION: SOURCE_MARKERS[channel.source], **channel.extensions}
                if channel.source in SOURCE_MARKERS
                else dict(channel.extensions)
            ),
        )
        for channel in discovered
    }
    document.channels.update(channels)
    return channels


def _populate_operations(
    document: AsyncAPI,
    discovered: list[DiscoveredChannel],
    channels: dict[str, Channel],
    *,
    config: "AsyncAPIConfig",
    schema_generator: AsyncAPISchemaGenerator,
    app: "Litestar",
) -> None:
    """Add every operation and its messages, then resolve replies given by name against the final message keys."""
    replies: list[tuple[Operation, ReplyDefinition, str]] = []
    used_operation_ids: set[str] = set()
    used_operation_keys: set[str] = set()
    channel_message_keys: dict[str, set[str]] = {}
    named_messages: dict[tuple[str, str], tuple[str, str]] = {}
    operation_traits = set(document.components.operation_traits)
    message_traits = set(document.components.message_traits)

    for discovered_channel in discovered:
        channel_key = discovered_channel.key
        channel_ref = Reference(ref=f"#/channels/{_json_pointer_escape(channel_key)}")
        channel = channels[channel_key]
        for discovered_operation, prepared_messages in _prepare_operations(
            discovered_channel, schema_generator=schema_generator, app=app, config=config, message_traits=message_traits
        ):
            default_operation_id = _default_operation_id(channel_key, OperationAction(discovered_operation.action))
            operation_id, operation_key = _ensure_unique_operation_id(
                discovered_operation.operation_id or default_operation_id,
                default_operation_id=default_operation_id,
                used_ids=used_operation_ids,
                used_keys=used_operation_keys,
                config=config,
            )
            used_operation_ids.add(operation_id.casefold())
            used_operation_keys.add(operation_key.casefold())

            messages: list[Message | Reference] = []
            for definition, message in prepared_messages:
                channel.messages = channel.messages or {}
                named_key = (channel_key, definition.name if definition.name is not None else f"@{operation_key}")
                existing = named_messages.get(named_key)
                if existing is not None:
                    message_key, source = existing
                    if _definition_key(channel.messages[message_key]) != _definition_key(message):
                        detail = f"Conflicting message {definition.name!r} on channel {channel_key!r}: {source} and {getattr(discovered_operation, 'provenance', discovered_channel.provenance)}"
                        raise ImproperlyConfiguredException(detail)
                else:
                    message_key = _ensure_unique_message_key(
                        definition.name or operation_key, channel_message_keys.setdefault(channel_key, set())
                    )
                    channel.messages[message_key] = message
                    named_messages[named_key] = (
                        message_key,
                        getattr(discovered_operation, "provenance", discovered_channel.provenance),
                    )
                reference = Reference(
                    ref=f"#/channels/{_json_pointer_escape(channel_key)}/messages/{_json_pointer_escape(message_key)}"
                )
                if reference not in messages:
                    messages.append(reference)

            operation_trait_refs = (
                _resolve_operation_traits(discovered_operation.traits, available=operation_traits)
                if discovered_operation.traits
                else None
            )

            provenance = getattr(discovered_operation, "provenance", discovered_channel.provenance)
            operation = Operation(
                action=OperationAction(discovered_operation.action),
                channel=channel_ref,
                title=discovered_operation.title,
                summary=discovered_operation.summary,
                description=discovered_operation.description,
                messages=messages,
                traits=operation_trait_refs,
                tags=discovered_operation.tags,
                security=_resolve_names(
                    discovered_operation.security,
                    available=document.components.security_schemes,
                    kind="security scheme",
                    pointer="#/components/securitySchemes",
                    context=f" in {provenance}",
                ),
                bindings=discovered_operation.bindings,
                reply=None if isinstance(discovered_operation.reply, ReplyDefinition) else discovered_operation.reply,
            )
            document.operations[operation_key] = operation
            if isinstance(discovered_operation.reply, ReplyDefinition):
                replies.append((operation, discovered_operation.reply, provenance))

    for operation, reply, provenance in replies:
        operation.reply = _resolve_reply(reply, channels=channels, provenance=provenance)


def _resolve_names(
    values: "Sequence[str | T | Reference] | None", *, available: dict[str, Any], kind: str, pointer: str, context: str
) -> "list[T | Reference] | None":
    """Replace names with references to ``pointer/<name>``, raising for names missing from ``available``."""
    if values is None:
        return None
    resolved: list[T | Reference] = []
    for value in values:
        if not isinstance(value, str):
            resolved.append(value)
            continue
        if value not in available:
            message = f"Unknown {kind} {value!r}{context}; valid names: {sorted(available)!r}"
            raise ImproperlyConfiguredException(message)
        resolved.append(Reference(ref=f"{pointer}/{_json_pointer_escape(value)}"))
    return resolved


def _resolve_reply(reply: ReplyDefinition, *, channels: dict[str, Channel], provenance: str) -> Reply:
    channel = channels.get(reply.channel)
    if channel is None:
        message = f"Unknown reply channel {reply.channel!r} in {provenance}; valid names: {sorted(channels)!r}"
        raise ImproperlyConfiguredException(message)
    channel_pointer = f"#/channels/{_json_pointer_escape(reply.channel)}"
    return Reply(
        address=reply.address,
        channel=Reference(ref=channel_pointer),
        messages=_resolve_names(
            reply.messages,
            available=channel.messages or {},
            kind="reply message",
            pointer=f"{channel_pointer}/messages",
            context=f" on channel {reply.channel!r} in {provenance}",
        ),
    )


def _prepare_operations(
    channel: DiscoveredChannel,
    *,
    schema_generator: AsyncAPISchemaGenerator,
    app: "Litestar",
    config: "AsyncAPIConfig",
    message_traits: set[str],
) -> list[tuple[OperationDefinition, list[tuple[MessageDefinition, Message]]]]:
    """Order operations by their assembled contracts, including encoded literal examples."""
    prepared = []
    for operation in sorted(channel.operations, key=_definition_key):
        messages = [
            (
                definition,
                _build_message(
                    definition,
                    schema_generator=schema_generator,
                    app=app,
                    config=config,
                    provenance=getattr(operation, "provenance", channel.provenance),
                    message_traits=message_traits,
                ),
            )
            for definition in sorted(operation.messages or [], key=_definition_key)
        ]
        messages.sort(key=lambda pair: _definition_key(pair[1]))
        prepared.append((operation, messages))
    return sorted(
        prepared,
        key=lambda pair: (
            _definition_key(replace(pair[0], messages=None)),
            _definition_key([message for _, message in pair[1]]),
        ),
    )


def _resolve_operation_traits(
    traits: list[str | OperationTrait | Reference], *, available: set[str]
) -> "list[OperationTrait | Reference]":
    missing = [name for name in traits if isinstance(name, str) and name not in available]
    if missing:
        msg = f"Unknown operation traits referenced: {missing!r}. Register them on AsyncAPIConfig.operation_traits."
        raise ImproperlyConfiguredException(msg)
    return [
        Reference(ref=f"#/components/operationTraits/{_json_pointer_escape(name)}") if isinstance(name, str) else name
        for name in traits
    ]


def _resolve_message_traits(
    traits: list[str | MessageTrait | Reference], *, available: set[str]
) -> "list[MessageTrait | Reference]":
    missing = [name for name in traits if isinstance(name, str) and name not in available]
    if missing:
        msg = f"Unknown message traits referenced: {missing!r}. Register them on AsyncAPIConfig.message_traits."
        raise ImproperlyConfiguredException(msg)
    return [
        Reference(ref=f"#/components/messageTraits/{_json_pointer_escape(name)}") if isinstance(name, str) else name
        for name in traits
    ]


def _build_message(
    definition: MessageDefinition,
    *,
    schema_generator: AsyncAPISchemaGenerator,
    app: "Litestar",
    config: "AsyncAPIConfig",
    provenance: str,
    message_traits: set[str],
) -> Message:

    def schema(value: object | None) -> Any:
        if value is None or isinstance(value, (Schema, Reference, dict, bool, MultiFormatSchema)):
            return value
        return schema_generator.generate(value, provenance=provenance)

    payload = schema(definition.payload)
    examples = definition.examples
    if (
        examples is None
        and definition.payload is not None
        and not isinstance(definition.payload, (Schema, Reference, dict, bool, MultiFormatSchema, NativeDTOPayload))
    ):
        examples = schema_generator.declared_examples(definition.payload)
        if examples is None:
            example = generate_example(resolve_annotation(definition.payload, app), config=config, app=app)
            examples = [example] if example is not UNSET else None
    if examples is None and isinstance(definition.payload, NativeDTOPayload) and config.create_examples:
        warnings.warn(
            f"Omitting automatic AsyncAPI example for native DTO at {provenance}; provide an explicit transferred example",
            stacklevel=2,
        )
    return Message(
        payload=payload,
        headers=schema(definition.headers),
        name=definition.name,
        title=definition.title,
        summary=definition.summary,
        description=definition.description,
        examples=normalize_examples(cast("list[Any]", examples), app=app) if examples is not None else None,
        content_type=definition.content_type or _infer_content_type(payload),
        correlation_id=definition.correlation_id,
        traits=_resolve_message_traits(definition.traits, available=message_traits)
        if definition.traits is not None
        else None,
        bindings=definition.bindings,
        tags=definition.tags,
        extensions=definition.extensions,
    )


def _infer_content_type(payload: Schema | Reference | dict[str, Any] | bool) -> str | None:
    value = payload.to_schema() if isinstance(payload, (Schema, Reference)) else payload
    if not isinstance(value, dict):
        return None
    raw_types = value.get("type")
    schema_types = raw_types if isinstance(raw_types, list) else [raw_types]
    if (
        "$ref" in value
        or "properties" in value
        or "items" in value
        or "object" in schema_types
        or "array" in schema_types
    ):
        return "application/json"
    return None


def _definition_key(value: Any) -> str:
    """Order definitions by stable public values, never object identities."""

    def stable(item: Any) -> Any:
        result: Any
        if isinstance(item, FieldDefinition):
            result = {
                "annotation": stable(item.annotation),
                "name": item.name,
                "default": stable(item.default),
                "metadata": stable(item.metadata),
                "extra": stable(item.extra),
                "kwarg": stable(item.kwarg_definition),
            }
        elif isinstance(item, NativeDTOPayload):
            result = [stable(item.field), stable(item.dto), stable(item.dto.config)]
        elif isinstance(item, type):
            result = f"{item.__module__}.{item.__qualname__}"
        elif isinstance(item, BaseSchemaObject):
            result = stable(item.to_schema())
        elif is_dataclass(item):
            result = {
                field.name: stable(getattr(item, field.name))
                for field in fields(item)
                if field.name not in {"provenance", "route_identity"}
            }
        elif isinstance(item, dict):
            result = {str(key): stable(value) for key, value in sorted(item.items(), key=lambda pair: str(pair[0]))}
        elif isinstance(item, (set, frozenset)):
            result = sorted((stable(value) for value in item), key=str)
        elif isinstance(item, (list, tuple)):
            result = [stable(value) for value in item]
        elif isinstance(item, bytes):
            result = {"bytes": item.hex()}
        elif item is None or isinstance(item, (str, int, float, bool)):
            result = item
        else:
            result = (
                str(item)
                if type(item).__module__ in {"typing", "types", "decimal", "uuid", "datetime"}
                else f"{type(item).__module__}.{type(item).__qualname__}"
            )

        return result

    return json.dumps(stable(value), sort_keys=True, ensure_ascii=True)


def _merge_components(
    target: dict[str, Any], additions: dict[str, Any], category: str, *, source: str | None = None
) -> None:
    for key, value in additions.items():
        if key in target and _definition_key(target[key]) != _definition_key(value):
            message = (
                f"Conflicting component {category}/{key}: AsyncAPIConfig.components and "
                f"{source or f'generated/configured {category}'}"
            )
            raise ImproperlyConfiguredException(message)
        target[key] = value


def _normalize_channels(channels: list[DiscoveredChannel]) -> list[DiscoveredChannel]:
    """Order channels by key and reject two channels that claim the same key."""
    normalized: dict[str, DiscoveredChannel] = {}
    for channel in sorted(channels, key=lambda value: (value.key, value.provenance)):
        previous = normalized.get(channel.key)
        if previous is not None:
            detail = f"Conflicting channel {channel.key!r}: {previous.provenance} and {channel.provenance}"
            raise ImproperlyConfiguredException(detail)
        normalized[channel.key] = channel
    return list(normalized.values())


def _reference_index(
    document: dict[str, Any],
) -> tuple[
    dict[tuple[str, ...], str],
    dict[tuple[str, ...], dict[str, Any]],
    list[tuple[tuple[str, ...], str, str, tuple[str, ...] | None]],
]:
    """Validate known AsyncAPI reference positions without traversing literal payload data."""
    kinds: dict[tuple[str, ...], str] = {}
    objects: dict[tuple[str, ...], dict[str, Any]] = {}
    references: list[tuple[tuple[str, ...], str, str, tuple[str, ...] | None]] = []
    component_kinds = {
        "schemas": "schema",
        "messages": "message",
        "messageTraits": "messageTrait",
        "operationTraits": "operationTrait",
        "securitySchemes": "security",
        "parameters": "parameter",
        "correlationIds": "correlationId",
        "operations": "operation",
        "channels": "channel",
        "servers": "server",
        "replies": "reply",
        "replyAddresses": "replyAddress",
        "serverVariables": "serverVariable",
        "tags": "tag",
        "externalDocs": "externalDocs",
        "serverBindings": "serverBindings",
        "channelBindings": "channelBindings",
        "operationBindings": "operationBindings",
        "messageBindings": "messageBindings",
    }
    fields_by_kind = {
        "channel": {"messages": ("message", "map"), "parameters": ("parameter", "map"), "servers": ("server", "list")},
        "operation": {
            "channel": ("channel", "one"),
            "messages": ("message", "list"),
            "traits": ("operationTrait", "list"),
            "reply": ("reply", "one"),
            "security": ("security", "list"),
        },
        "operationTrait": {"security": ("security", "list")},
        "message": {
            "payload": ("schema", "one"),
            "headers": ("schema", "one"),
            "traits": ("messageTrait", "list"),
            "correlationId": ("correlationId", "one"),
        },
        "messageTrait": {"headers": ("schema", "one"), "correlationId": ("correlationId", "one")},
        "server": {"variables": ("serverVariable", "map"), "security": ("security", "list")},
        "reply": {"channel": ("channel", "one"), "messages": ("message", "list"), "address": ("replyAddress", "one")},
    }

    def visit(value: Any, kind: str, path: tuple[str, ...], schema_base: tuple[str, ...] | None = None) -> None:
        kinds[path] = kind
        if not isinstance(value, dict):
            return
        objects[path] = value
        if kind == "schema":
            schema_base = schema_base or path
            if "schemaFormat" in value:
                return
        if "$ref" in value:
            references.append((path, kind, value["$ref"], schema_base))
            return
        if kind == "schema":
            for name in ("properties", "patternProperties", "definitions", "$defs", "dependentSchemas", "dependencies"):
                for key, child in value.get(name, {}).items():
                    if isinstance(child, (dict, bool)):
                        visit(child, "schema", (*path, name, key), schema_base)
            for name in (
                "items",
                "additionalItems",
                "additionalProperties",
                "contains",
                "propertyNames",
                "not",
                "if",
                "then",
                "else",
                "allOf",
                "anyOf",
                "oneOf",
                "prefixItems",
            ):
                child = value.get(name)
                if isinstance(child, list):
                    for index, item in enumerate(child):
                        visit(item, "schema", (*path, name, str(index)), schema_base)
                elif isinstance(child, (dict, bool)):
                    visit(child, "schema", (*path, name), schema_base)
            return
        children = dict(fields_by_kind.get(kind, {}))
        if kind in {"channel", "operation", "operationTrait", "message", "messageTrait", "server"}:
            children.update(tags=("tag", "list"), externalDocs=("externalDocs", "one"))
            children["bindings"] = (kind.removesuffix("Trait") + "Bindings", "one")
        for name, (child_kind, container) in children.items():
            child = value.get(name)
            if child is None:
                continue
            if container == "map":
                for key, item in child.items():
                    visit(item, child_kind, (*path, name, key))
            elif container == "list":
                for index, item in enumerate(child):
                    visit(item, child_kind, (*path, name, str(index)))
            else:
                visit(child, child_kind, (*path, name))

    for name, kind in (("channels", "channel"), ("operations", "operation"), ("servers", "server")):
        for key, value in document.get(name, {}).items():
            visit(value, kind, (name, key))
    for name, kind in component_kinds.items():
        for key, value in document.get("components", {}).get(name, {}).items():
            visit(value, kind, ("components", name, key))

    return kinds, objects, references


def _reference_error(message: str) -> NoReturn:
    raise ImproperlyConfiguredException(message)


def _validate_references(document: dict[str, Any]) -> None:
    """Resolve local typed references and enforce root and selected-channel restrictions."""
    kinds, objects, references = _reference_index(document)

    def pointer(ref: str, base: tuple[str, ...] | None = None) -> tuple[str, ...]:
        fragment = unquote(ref[1:])
        if fragment and not fragment.startswith("/"):
            _reference_error(f"Unsupported local reference {ref!r}: expected a JSON Pointer")
        tokens = tuple(fragment[1:].split("/")) if fragment else ()
        if any(re.search(r"~(?![01])", token) for token in tokens):
            _reference_error(f"Invalid JSON Pointer escaping in {ref!r}")
        path = tuple(token.replace("~1", "/").replace("~0", "~") for token in tokens)
        if base is not None and path not in kinds:
            return (*base, *path)
        return path

    def resolve(
        ref: str, kind: str, source: tuple[str, ...], base: tuple[str, ...] | None
    ) -> tuple[tuple[str, ...], tuple[str, ...] | None] | None:
        if not isinstance(ref, str):
            _reference_error(f"Invalid reference at {'/'.join(source)}: expected a string")
        if not ref.startswith("#"):
            return None
        path = pointer(ref, base)
        initial = path
        seen: set[tuple[str, ...]] = set()
        while True:
            if path in seen:
                _reference_error(f"Cyclic local reference {ref!r} at {'/'.join(source)}")
            seen.add(path)
            if kinds.get(path) != kind:
                _reference_error(
                    f"Invalid {kind} reference {ref!r} at {'/'.join(source)}: target is missing or has the wrong type/location"
                )
            target = objects.get(path, {})
            if "$ref" not in target:
                return initial, path
            next_ref = target["$ref"]
            if not next_ref.startswith("#"):
                return initial, None
            path = pointer(next_ref, base)

    for path, kind, ref, base in references:
        resolved = resolve(ref, kind, path, base)
        if resolved is None:
            continue
        target, terminal = resolved
        root_channel = path[:1] == ("channels",)
        if root_channel and path[2:3] == ("servers",) and target[:-1] != ("servers",):
            _reference_error(f"Channel server reference {ref!r} at {'/'.join(path)} must select a root server")
        if kind == "channel" and path[-1] == "channel" and path[0] == "operations" and target[:-1] != ("channels",):
            _reference_error(f"Operation channel reference {ref!r} must select a root channel")
        if kind == "message" and path[-2:-1] == ("messages",) and path[-1].isdigit():
            owner = objects.get(path[:-2], {})
            channel_ref = owner.get("channel", {}).get("$ref")
            if channel_ref is not None and channel_ref.startswith("#"):
                selected = resolve(channel_ref, "channel", path, None)
                channel_path = selected[1] if selected is not None else None
                if channel_path is None or terminal is None:
                    continue
                available = {
                    selected_message[1]
                    for name in objects[channel_path].get("messages", {})
                    if (
                        selected_message := resolve(
                            "#/" + "/".join(_json_pointer_escape(token) for token in (*channel_path, "messages", name)),
                            "message",
                            path,
                            None,
                        )
                    )
                    is not None
                }
                if terminal not in available:
                    _reference_error(
                        f"Message reference {ref!r} at {'/'.join(path)} does not belong to its selected channel"
                    )
