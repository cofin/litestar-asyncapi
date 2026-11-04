import warnings
from dataclasses import fields, replace
from typing import TYPE_CHECKING, Any

from litestar_asyncapi._compat import (
    generated_channels_mode,
    websocket_content_type,
    websocket_handler_name,
    websocket_payload,
    websocket_signature,
)
from litestar_asyncapi.asyncapi.datastructures import (
    DiscoveredChannel,
    DiscoveredOperation,
    DiscoverySource,
    MessageDefinition,
    OperationDefinition,
)
from litestar_asyncapi.spec import OperationAction, Parameter, Reference
from litestar_asyncapi.spec.bindings import WebSocketChannelBinding

if TYPE_CHECKING:
    from litestar import Litestar
    from litestar.handlers.websocket_handlers import WebsocketRouteHandler
    from litestar.types.internal_types import PathParameterDefinition

    from litestar_asyncapi import AsyncAPIConfig
    from litestar_asyncapi.asyncapi.schema_generation import AsyncAPISchemaGenerator


__all__ = ("extract_websocket_channels",)


def extract_websocket_channels(
    app: "Litestar", *, schema_generator: "AsyncAPISchemaGenerator", config: "AsyncAPIConfig | None" = None
) -> list[DiscoveredChannel]:
    """Extract websocket routes from a Litestar application.

    Args:
        app: Litestar application.
        schema_generator: Schema generator used to produce message/parameter schemas.
        config: Optional AsyncAPI configuration used to control docstring extraction.

    Returns:
        A list of discovered channels.
    """
    from litestar.routes.websocket import WebSocketRoute

    if config is None:
        from litestar_asyncapi import AsyncAPIConfig

        config = AsyncAPIConfig()

    if not config.include_websocket_routes:
        return []
    channels: list[DiscoveredChannel] = []
    for route in app.routes:
        if not isinstance(route, WebSocketRoute):
            continue

        if generated_channels_mode(route.route_handler, app) is not None or not _should_include_handler(
            route.route_handler
        ):
            continue

        parameters = _path_parameters_to_parameters(route.path_parameters)
        operations = _infer_operations_from_handler(
            route.route_handler, schema_generator=schema_generator, config=config, app=app
        )
        if not operations:
            continue
        for operation in operations:
            operation.provenance = f"route {route.path_format} handler {websocket_handler_name(route.route_handler)}"
        channels.append(
            DiscoveredChannel(
                route_identity=route,
                key=route.path_format,
                address=route.path_format,
                provenance=f"route {route.path_format} handler {websocket_handler_name(route.route_handler)}",
                source=DiscoverySource.WEBSOCKET,
                parameters=parameters or None,
                bindings={"ws": WebSocketChannelBinding()},
                operations=operations,
            )
        )

    return channels


def _should_include_handler(handler: "WebsocketRouteHandler") -> bool:
    """Honor the handler's resolved ``include_in_schema`` option, defaulting to inclusion.

    Returns:
        ``False`` only when ``include_in_schema`` is explicitly ``False``.
    """
    return handler.opt.get("include_in_schema") is not False


def _path_parameters_to_parameters(
    path_parameters: "dict[str, PathParameterDefinition]",
) -> dict[str, Parameter | Reference]:
    """Convert path parameters into AsyncAPI Parameter objects.

    AsyncAPI 3.0 parameters are simplified and always treated as strings.
    The original Python type name is recorded in the parameter description for clarity.
    """
    parameters: dict[str, Parameter | Reference] = {}
    for name, param in path_parameters.items():
        type_name = param.type.__name__ if hasattr(param.type, "__name__") else str(param.type)
        parameters[name] = Parameter(description=f"Path parameter: {name} (type: {type_name})")
    return parameters


def _infer_operations_from_handler(
    route_handler: "WebsocketRouteHandler",
    *,
    schema_generator: "AsyncAPISchemaGenerator",
    config: "AsyncAPIConfig",
    app: "Litestar",
) -> list[DiscoveredOperation]:
    from litestar_asyncapi.decorators import ASYNCAPI_OPT_KEY, AsyncAPIMetadata

    signature = websocket_signature(route_handler)
    if signature is not None:
        receive, send, receive_mode, send_mode = signature
        operations = [
            DiscoveredOperation(
                action=action,
                provenance=websocket_handler_name(route_handler),
                operation_id=f"{websocket_handler_name(route_handler)}_{action.value}",
                messages=[
                    MessageDefinition(
                        payload=websocket_payload(route_handler, field, sending=action is OperationAction.SEND),
                        content_type=websocket_content_type(
                            route_handler, field, sending=action is OperationAction.SEND
                        ),
                        extensions={"x-websocket-mode": mode},
                    )
                ],
            )
            for action, field, mode in (
                (OperationAction.RECEIVE, receive, receive_mode),
                (OperationAction.SEND, send, send_mode),
            )
            if field is not None and not (action is OperationAction.SEND and field.is_none_type)
        ]
        operations = _apply_decorator_overrides(
            route_handler, operations, schema_generator=schema_generator, config=config, app=app
        )
    else:
        metadata = route_handler.opt.get(ASYNCAPI_OPT_KEY)
        explicit = isinstance(metadata, AsyncAPIMetadata) and bool(metadata.operations)
        if not explicit and not config.include_raw_websocket_routes:
            return []
        operations = _apply_decorator_overrides(
            route_handler,
            _infer_raw_websocket_operations(route_handler),
            schema_generator=schema_generator,
            config=config,
            app=app,
            replace_placeholders=True,
        )
        if any(message.payload is None for operation in operations for message in operation.messages or []):
            warnings.warn(
                f"AsyncAPI cannot infer the raw WebSocket payload for {sorted(route_handler.paths)!r} handler {websocket_handler_name(route_handler)}; emitting an unconstrained message",
                stacklevel=2,
            )
    _apply_handler_metadata(route_handler, operations)
    _apply_docstring_descriptions(route_handler, operations, config=config)
    return operations


def _apply_decorator_overrides(
    route_handler: Any,
    operations: list[DiscoveredOperation],
    *,
    schema_generator: "AsyncAPISchemaGenerator",
    config: "AsyncAPIConfig",
    app: "Litestar",
    replace_placeholders: bool = False,
) -> list[DiscoveredOperation]:
    from litestar_asyncapi.decorators import ASYNCAPI_OPT_KEY, AsyncAPIMetadata

    raw_metadata = route_handler.opt.get(ASYNCAPI_OPT_KEY)
    if not isinstance(raw_metadata, AsyncAPIMetadata) or not raw_metadata.operations:
        return operations
    if replace_placeholders:
        operations = []
    by_action = {op.action: op for op in operations}
    for action, override in raw_metadata.operations.items():
        operation = by_action.get(action)
        if operation is None:
            operation = DiscoveredOperation(action=action, provenance=str(route_handler))
            operations.append(operation)
        for item in fields(OperationDefinition):
            value = getattr(override, item.name)
            if item.name != "messages" and value is not None:
                setattr(operation, item.name, value)
        if override.messages is not None:
            inferred = operation.messages[0] if operation.messages else MessageDefinition()
            operation.messages = [
                replace(
                    message,
                    payload=message.payload if message.payload is not None else inferred.payload,
                    content_type=message.content_type if message.content_type is not None else inferred.content_type,
                    extensions={**inferred.extensions, **message.extensions},
                )
                for message in override.messages
            ]
    return operations


def _infer_raw_websocket_operations(route_handler: Any) -> list[DiscoveredOperation]:
    """Create minimal placeholder operations for raw @websocket handlers.

    Raw websocket handlers don't have typed data parameters, so we create
    placeholder operations that indicate bidirectional communication is possible.

    Args:
        route_handler: The websocket route handler.

    Returns:
        A list containing receive and send operations with generic schemas.
    """
    handler_name = getattr(route_handler, "handler_name", "websocket")
    return [
        DiscoveredOperation(
            provenance=str(route_handler),
            action=OperationAction.RECEIVE,
            operation_id=f"{handler_name}_receive",
            summary="Receive message",
            messages=[
                MessageDefinition(
                    name="RawMessage",
                    summary="Raw WebSocket message",
                    description="This endpoint uses raw WebSocket handling. Message format depends on implementation.",
                )
            ],
        ),
        DiscoveredOperation(
            provenance=str(route_handler),
            action=OperationAction.SEND,
            operation_id=f"{handler_name}_send",
            summary="Send message",
            messages=[
                MessageDefinition(
                    name="RawResponse",
                    summary="Raw WebSocket response",
                    description="This endpoint uses raw WebSocket handling. Response format depends on implementation.",
                )
            ],
        ),
    ]


def _apply_handler_metadata(route_handler: Any, operations: list[DiscoveredOperation]) -> None:
    """Fill operation fields the decorators left empty from the handler's own metadata.

    The handler ``operation_id`` replaces the inferred id of every operation without a decorator
    ``operation_id`` and is suffixed with the action when the handler documents several operations.
    """
    from litestar_asyncapi.decorators import ASYNCAPI_OPT_KEY, AsyncAPIMetadata

    summary = _get_handler_string_attribute(route_handler, "summary")
    description = _get_handler_string_attribute(route_handler, "description")
    operation_id = _get_handler_string_attribute(route_handler, "operation_id")
    metadata = route_handler.opt.get(ASYNCAPI_OPT_KEY)
    decorated_ids = (
        {action for action, override in metadata.operations.items() if override.operation_id is not None}
        if isinstance(metadata, AsyncAPIMetadata)
        else set()
    )

    for operation in operations:
        if summary is not None and operation.summary is None:
            operation.summary = summary
        if description is not None and operation.description is None:
            operation.description = description
        if operation_id is not None and operation.action not in decorated_ids:
            operation.operation_id = (
                f"{operation_id}_{OperationAction(operation.action).value}" if len(operations) > 1 else operation_id
            )


def _apply_docstring_descriptions(
    route_handler: Any, operations: list[DiscoveredOperation], *, config: "AsyncAPIConfig"
) -> None:
    if not config.use_handler_docstrings or not operations:
        return

    from litestar_asyncapi.asyncapi.utils.docstrings import get_handler_docstring

    docstring = get_handler_docstring(route_handler)
    if not docstring:
        return

    for operation in operations:
        if operation.description is None:
            operation.description = docstring


def _get_handler_string_attribute(route_handler: Any, name: str) -> str | None:
    value = getattr(route_handler, name, None)
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    if hasattr(route_handler, "opt") and isinstance(route_handler.opt, dict):
        opt_value = route_handler.opt.get(name)
        if isinstance(opt_value, str):
            stripped = opt_value.strip()
            return stripped or None
    return None
