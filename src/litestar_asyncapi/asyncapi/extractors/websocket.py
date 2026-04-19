from typing import TYPE_CHECKING, Any, cast

from litestar.types.builtin_types import NoneType
from litestar.typing import FieldDefinition

from litestar_asyncapi.asyncapi.datastructures import (
    DiscoveredChannel,
    DiscoveredMessage,
    DiscoveredOperation,
    DiscoverySource,
)
from litestar_asyncapi.spec import OperationAction, Parameter, Reference, Schema, SchemaType

if TYPE_CHECKING:
    from litestar import Litestar
    from litestar.handlers.websocket_handlers import WebsocketRouteHandler
    from litestar.types.internal_types import PathParameterDefinition

    from litestar_asyncapi import AsyncAPIConfig
    from litestar_asyncapi.asyncapi.schema_generation import AsyncAPISchemaGenerator


__all__ = ("extract_websocket_channels",)


def extract_websocket_channels(
    app: "Litestar",
    *,
    schema_generator: "AsyncAPISchemaGenerator",
    config: "AsyncAPIConfig | None" = None,
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

    channels: list[DiscoveredChannel] = []
    for route in app.routes:
        if not isinstance(route, WebSocketRoute):
            continue

        if not _should_include_handler(route.route_handler):
            continue

        parameters = _path_parameters_to_parameters(route.path_parameters, schema_generator=schema_generator)
        operations = _infer_operations_from_handler(
            route.route_handler,
            schema_generator=schema_generator,
            config=config,
        )
        channels.append(
            DiscoveredChannel(
                address=route.path_format,
                source=DiscoverySource.WEBSOCKET,
                parameters=parameters or None,
                operations=operations,
            )
        )

    return channels


def _should_include_handler(handler: "WebsocketRouteHandler") -> bool:
    """Determine if a websocket route handler should be included in the AsyncAPI schema.

    Checks the 'include_in_schema' option in the handler's 'opt' dictionary, defaulting to True
    if not explicitly set (mirroring Litestar's HTTP handler behavior).
    """
    if hasattr(handler, "opt") and isinstance(handler.opt, dict):
        include_in_schema = handler.opt.get("include_in_schema")
        if isinstance(include_in_schema, bool):
            return include_in_schema
    return True


def _path_parameters_to_parameters(
    path_parameters: "dict[str, PathParameterDefinition]", *, schema_generator: "AsyncAPISchemaGenerator"
) -> dict[str, Parameter]:
    parameters: dict[str, Parameter] = {}
    for name, param in path_parameters.items():
        schema = schema_generator.generate_schema(FieldDefinition.from_annotation(param.type))
        parameters[name] = Parameter(schema=schema, location="path")
    return parameters


def _infer_operations_from_handler(
    route_handler: "WebsocketRouteHandler",
    *,
    schema_generator: "AsyncAPISchemaGenerator",
    config: "AsyncAPIConfig",
) -> list[DiscoveredOperation]:
    from litestar.handlers.websocket_handlers.listener import WebsocketListenerRouteHandler
    from litestar.handlers.websocket_handlers.stream import WebSocketStreamHandler

    operations: list[DiscoveredOperation]

    if isinstance(route_handler, WebsocketListenerRouteHandler):
        operations = _infer_listener_operations(route_handler, schema_generator=schema_generator, config=config)
        _apply_docstring_descriptions(route_handler, operations, config=config)
        return _apply_decorator_overrides(route_handler, operations, schema_generator=schema_generator)

    if isinstance(route_handler, WebSocketStreamHandler):
        operations = _infer_stream_operations(route_handler, schema_generator=schema_generator, config=config)
        _apply_docstring_descriptions(route_handler, operations, config=config)
        return _apply_decorator_overrides(route_handler, operations, schema_generator=schema_generator)

    operations = _infer_raw_websocket_operations(route_handler)
    _apply_handler_metadata(route_handler, operations, include_action_suffix=True)
    _apply_docstring_descriptions(route_handler, operations, config=config)
    return _apply_decorator_overrides(
        route_handler, operations, schema_generator=schema_generator, replace_placeholders=True
    )


def _apply_decorator_overrides(
    route_handler: Any,
    operations: list[DiscoveredOperation],
    *,
    schema_generator: "AsyncAPISchemaGenerator",
    replace_placeholders: bool = False,
) -> list[DiscoveredOperation]:
    from litestar_asyncapi.decorators import ASYNCAPI_OPT_KEY, AsyncAPIMetadata

    raw_metadata = route_handler.opt.get(ASYNCAPI_OPT_KEY)
    if not isinstance(raw_metadata, AsyncAPIMetadata) or not raw_metadata.operations:
        return operations

    # If we have explicit decorators and should replace placeholders, start fresh
    if replace_placeholders:
        operations = []

    by_action = {op.action: op for op in operations}

    for action, override in raw_metadata.operations.items():
        op = by_action.get(action)
        if op is None:
            op = DiscoveredOperation(action=action)
            operations.append(op)
            by_action[action] = op

        if override.operation_id is not None:
            op.operation_id = override.operation_id
        if override.title is not None:
            op.title = override.title
        if override.summary is not None:
            op.summary = override.summary
        if override.description is not None:
            op.description = override.description
        if override.traits is not None:
            op.traits = override.traits

        if override.message is None:
            continue

        message = op.message or DiscoveredMessage()
        if override.message.payload is not None:
            payload = schema_generator.generate_schema(FieldDefinition.from_annotation(override.message.payload))
            message.payload = payload
            if override.message.content_type is None:
                message.content_type = _infer_content_type(payload)

        if override.message.name is not None:
            message.name = override.message.name
        if override.message.title is not None:
            message.title = override.message.title
        if override.message.summary is not None:
            message.summary = override.message.summary
        if override.message.description is not None:
            message.description = override.message.description
        if override.message.examples is not None:
            message.examples = override.message.examples
        if override.message.headers is not None:
            headers = schema_generator.generate_schema(FieldDefinition.from_annotation(override.message.headers))
            message.headers = headers
        if override.message.content_type is not None:
            message.content_type = override.message.content_type
        if override.message.traits is not None:
            message.traits = override.message.traits

        op.message = message

    return operations


def _infer_listener_operations(
    route_handler: Any,
    *,
    schema_generator: "AsyncAPISchemaGenerator",
    config: "AsyncAPIConfig",
) -> list[DiscoveredOperation]:
    # These are set by Litestar during handler registration.
    data_field = cast("FieldDefinition", route_handler._parsed_data_field)
    return_field = cast("FieldDefinition", route_handler._parsed_return_field)

    operations: list[DiscoveredOperation] = []
    receive_payload = schema_generator.generate_schema(data_field)
    receive_example = _generate_example(data_field, config=config)
    operations.append(
        DiscoveredOperation(
            action=OperationAction.RECEIVE,
            operation_id=f"{route_handler.handler_name}_receive",
            message=DiscoveredMessage(
                payload=receive_payload,
                content_type=_infer_content_type(receive_payload),
                examples=[receive_example] if receive_example is not None else None,
            ),
        )
    )

    if not _is_none_return_type(return_field):
        send_payload = schema_generator.generate_schema(return_field)
        send_example = _generate_example(return_field, config=config)
        operations.append(
            DiscoveredOperation(
                action=OperationAction.SEND,
                operation_id=f"{route_handler.handler_name}_send",
                message=DiscoveredMessage(
                    payload=send_payload,
                    content_type=_infer_content_type(send_payload),
                    examples=[send_example] if send_example is not None else None,
                ),
            )
        )

    _apply_handler_metadata(route_handler, operations, include_action_suffix=True)
    return operations


def _infer_stream_operations(
    route_handler: Any,
    *,
    schema_generator: "AsyncAPISchemaGenerator",
    config: "AsyncAPIConfig",
) -> list[DiscoveredOperation]:
    return_field = cast("FieldDefinition", route_handler._parsed_return_field)

    payload = schema_generator.generate_schema(return_field)
    example = _generate_example(return_field, config=config)
    operations = [
        DiscoveredOperation(
            action=OperationAction.SEND,
            operation_id=f"{route_handler.handler_name}_send",
            message=DiscoveredMessage(
                payload=payload,
                content_type=_infer_content_type(payload),
                examples=[example] if example is not None else None,
            ),
        )
    ]
    _apply_handler_metadata(route_handler, operations, include_action_suffix=False)
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
            action=OperationAction.RECEIVE,
            operation_id=f"{handler_name}_receive",
            summary="Receive message",
            message=DiscoveredMessage(
                name="RawMessage",
                summary="Raw WebSocket message",
                description="This endpoint uses raw WebSocket handling. Message format depends on implementation.",
            ),
        ),
        DiscoveredOperation(
            action=OperationAction.SEND,
            operation_id=f"{handler_name}_send",
            summary="Send message",
            message=DiscoveredMessage(
                name="RawResponse",
                summary="Raw WebSocket response",
                description="This endpoint uses raw WebSocket handling. Response format depends on implementation.",
            ),
        ),
    ]


def _apply_handler_metadata(
    route_handler: Any, operations: list[DiscoveredOperation], *, include_action_suffix: bool
) -> None:
    summary = _get_handler_string_attribute(route_handler, "summary")
    description = _get_handler_string_attribute(route_handler, "description")
    operation_id = _get_handler_string_attribute(route_handler, "operation_id")

    if not any((summary, description, operation_id)):
        return

    for operation in operations:
        if summary is not None and operation.summary is None:
            operation.summary = summary
        if description is not None and operation.description is None:
            operation.description = description
        if operation_id is not None:
            if include_action_suffix and len(operations) > 1:
                operation.operation_id = f"{operation_id}_{operation.action.value}"
            else:
                operation.operation_id = operation_id


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


def _generate_example(field_definition: FieldDefinition, *, config: "AsyncAPIConfig") -> Any | None:
    if not config.create_examples:
        return None

    from litestar_asyncapi.asyncapi.utils.examples import generate_example

    return generate_example(field_definition, config=config)


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



def _is_none_return_type(field_definition: FieldDefinition) -> bool:
    return (
        field_definition.raw is None
        or field_definition.annotation is None
        or field_definition.is_subclass_of(NoneType)
        or field_definition.raw is NoneType
    )


def _infer_content_type(payload: Schema | Reference) -> str | None:
    # Until PRD-005 renderers are implemented, this is best-effort: treat objects/refs as JSON.
    if isinstance(payload, Reference):
        return "application/json"
    if payload.type is None:
        return None
    if payload.properties is not None or payload.items is not None:
        return "application/json"
    if payload.type in {SchemaType.OBJECT, SchemaType.ARRAY}:
        return "application/json"
    return None
