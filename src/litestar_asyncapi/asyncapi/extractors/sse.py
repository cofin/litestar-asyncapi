from typing import TYPE_CHECKING

from litestar.exceptions import ImproperlyConfiguredException
from litestar.response import ServerSentEvent
from litestar.routes import HTTPRoute, WebSocketRoute

from litestar_asyncapi.asyncapi.datastructures import (
    DiscoveredChannel,
    DiscoveredOperation,
    DiscoverySource,
    MessageDefinition,
)
from litestar_asyncapi.asyncapi.extractors.websocket import _apply_decorator_overrides, _path_parameters_to_parameters
from litestar_asyncapi.spec import OperationAction, Schema

if TYPE_CHECKING:
    from litestar import Litestar
    from litestar.handlers import HTTPRouteHandler

    from litestar_asyncapi import AsyncAPIConfig
    from litestar_asyncapi.asyncapi.schema_generation import AsyncAPISchemaGenerator

__all__ = ("extract_sse_channels",)

SSE_CONTENT_TYPE = "text/event-stream"


def extract_sse_channels(
    app: "Litestar", *, schema_generator: "AsyncAPISchemaGenerator", config: "AsyncAPIConfig | None" = None
) -> list[DiscoveredChannel]:
    """Describe HTTP routes that return ``ServerSentEvent`` as send-only channels.

    A route keeps its path as channel key unless a WebSocket route shares the path (``{path}:sse``) or
    several methods stream events (``{path}:sse:{method}``); the address is always the path. Only
    AsyncAPI decorator metadata is read, since HTTP ``summary``, ``description`` and ``operation_id``
    describe the HTTP operation.

    Args:
        app: Litestar application.
        schema_generator: Schema generator shared with the document build.
        config: Optional AsyncAPI configuration; ``include_sse_routes=False`` disables discovery.

    Returns:
        A list of discovered channels.

    Raises:
        ImproperlyConfiguredException: If a decorator declares a ``receive`` operation on an SSE route.
    """
    from litestar_asyncapi import AsyncAPIConfig
    from litestar_asyncapi.decorators import ASYNCAPI_OPT_KEY, AsyncAPIMetadata

    config = config or AsyncAPIConfig()
    if not config.include_sse_routes:
        return []
    socket_paths = {route.path_format for route in app.routes if isinstance(route, WebSocketRoute)}
    channels: list[DiscoveredChannel] = []
    for route in app.routes:
        if not isinstance(route, HTTPRoute):
            continue
        streams = sorted(
            (
                (method.lower(), handler)
                for handler in route.route_handlers
                if _is_server_sent_event_handler(handler)
                for method in handler.http_methods
            ),
            key=lambda pair: pair[0],
        )
        for method, handler in streams:
            if len(streams) > 1:
                key = f"{route.path_format}:sse:{method}"
            elif route.path_format in socket_paths:
                key = f"{route.path_format}:sse"
            else:
                key = route.path_format
            provenance = f"Server-Sent Event route {route.path_format} {method.upper()} handler {handler.handler_name}"
            metadata = handler.opt.get(ASYNCAPI_OPT_KEY)
            if isinstance(metadata, AsyncAPIMetadata) and OperationAction.RECEIVE in metadata.operations:
                detail = (
                    f"Server-Sent Event route {route.path_format} handler {handler.handler_name} declares a "
                    "receive operation; Server-Sent Event routes only send"
                )
                raise ImproperlyConfiguredException(detail)
            operations = _apply_decorator_overrides(
                handler,
                [
                    DiscoveredOperation(
                        action=OperationAction.SEND,
                        provenance=provenance,
                        messages=[MessageDefinition(payload=Schema(), content_type=SSE_CONTENT_TYPE)],
                    )
                ],
                schema_generator=schema_generator,
                config=config,
                app=app,
            )
            for operation in operations:
                operation.provenance = provenance
                for message in operation.messages or []:
                    message.content_type = SSE_CONTENT_TYPE
            channels.append(
                DiscoveredChannel(
                    route_identity=route,
                    key=key,
                    address=route.path_format,
                    source=DiscoverySource.SSE,
                    provenance=provenance,
                    parameters=_path_parameters_to_parameters(route.path_parameters) or None,
                    bindings={"http": {}},
                    operations=operations,
                )
            )
    return channels


def _is_server_sent_event_handler(handler: "HTTPRouteHandler") -> bool:
    """Select handlers whose resolved return annotation is ``ServerSentEvent`` and that stay in the schema.

    Returns:
        ``True`` for documented Server-Sent Event handlers.
    """
    return (
        handler.parsed_fn_signature.return_type.is_subclass_of(ServerSentEvent) and handler.resolve_include_in_schema()
    )
