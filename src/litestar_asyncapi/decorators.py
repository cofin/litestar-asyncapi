from collections.abc import Callable
from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING, Any, TypeVar

from litestar.exceptions import ImproperlyConfiguredException

from litestar_asyncapi._compat import websocket_handler_name
from litestar_asyncapi.asyncapi.datastructures import MessageDefinition, OperationDefinition
from litestar_asyncapi.spec import (
    CorrelationId,
    MessageTrait,
    OperationAction,
    OperationTrait,
    Reference,
    Reply,
    SecurityScheme,
    Tag,
)

__all__ = ("ASYNCAPI_OPT_KEY", "AsyncAPIMetadata", "asyncapi_message", "asyncapi_operation")


ASYNCAPI_OPT_KEY = "asyncapi"


if TYPE_CHECKING:
    from litestar.handlers.base import BaseRouteHandler

T = TypeVar("T")


@dataclass(slots=True)
class AsyncAPIMetadata:
    """Typed operation definitions attached to the native handler option layer."""

    operations: dict[OperationAction, OperationDefinition] = field(default_factory=dict)
    """Operation definitions keyed by action, written by the AsyncAPI decorators."""


def _get_route_handler(obj: object) -> "BaseRouteHandler":
    if not hasattr(obj, "opt"):
        msg = "AsyncAPI decorators must wrap a Litestar route handler."
        raise ImproperlyConfiguredException(msg)
    return obj  # type: ignore[return-value]


def _get_or_create_metadata(route_handler: "BaseRouteHandler") -> AsyncAPIMetadata:
    existing = route_handler.opt.get(ASYNCAPI_OPT_KEY)
    if isinstance(existing, AsyncAPIMetadata):
        return existing

    metadata = AsyncAPIMetadata()
    route_handler.opt[ASYNCAPI_OPT_KEY] = metadata
    return metadata


def asyncapi_operation(
    *,
    action: OperationAction | str,
    operation_id: str | None = None,
    title: str | None = None,
    summary: str | None = None,
    description: str | None = None,
    traits: list[str | OperationTrait | Reference] | None = None,
    messages: list[MessageDefinition] | None = None,
    tags: list[Tag | Reference] | None = None,
    security: list[SecurityScheme | Reference] | None = None,
    bindings: dict[str, Any] | Reference | None = None,
    reply: Reply | Reference | None = None,
) -> Callable[[T], T]:
    """Declare the operation for one action on a WebSocket or Server-Sent Event route handler.

    Keyword arguments match the fields of ``OperationDefinition``; ``None`` keeps the discovered value.
    Decorating the same handler again for the same action updates the declaration and appends messages.

    Returns:
        A decorator that mutates the Litestar route handler metadata in-place.
    """

    op_action = OperationAction(OperationDefinition(action=action).action)

    def decorator(obj: T) -> T:
        route_handler = _get_route_handler(obj)
        metadata = _get_or_create_metadata(route_handler)

        existing = metadata.operations.get(op_action) or OperationDefinition(action=op_action)
        changes: dict[str, Any] = {
            key: value
            for key, value in {
                "operation_id": operation_id,
                "title": title,
                "summary": summary,
                "description": description,
                "traits": traits,
                "tags": tags,
                "security": security,
                "bindings": bindings,
                "reply": reply,
            }.items()
            if value is not None
        }
        if messages is not None:
            changes["messages"] = [*(existing.messages or []), *messages]
        metadata.operations[op_action] = replace(existing, **changes)
        return obj

    return decorator


def asyncapi_message(
    *,
    action: OperationAction | str,
    payload: object | None = None,
    name: str | None = None,
    title: str | None = None,
    summary: str | None = None,
    description: str | None = None,
    examples: list[object] | None = None,
    headers: object | None = None,
    content_type: str | None = None,
    traits: list[str | MessageTrait | Reference] | None = None,
    correlation_id: CorrelationId | Reference | None = None,
    bindings: dict[str, Any] | Reference | None = None,
    tags: list[Tag | Reference] | None = None,
    extensions: dict[str, Any] | None = None,
) -> Callable[[T], T]:
    """Add a message to the operation for one action on a WebSocket or Server-Sent Event route handler.

    Keyword arguments match the fields of ``MessageDefinition``. A message without a ``name`` is
    rejected when the operation already has messages.

    Returns:
        A decorator that mutates the Litestar route handler metadata in-place.
    """

    op_action = OperationAction(OperationDefinition(action=action).action)

    def decorator(obj: T) -> T:
        route_handler = _get_route_handler(obj)
        metadata = _get_or_create_metadata(route_handler)

        operation = metadata.operations.get(op_action) or OperationDefinition(action=op_action)
        if name is None and operation.messages:
            msg = f"Ambiguous unnamed AsyncAPI message on {sorted(route_handler.paths)!r} handler {websocket_handler_name(route_handler)}: assign explicit message names"
            raise ImproperlyConfiguredException(msg)
        message = MessageDefinition(
            payload=payload,
            name=name,
            title=title,
            summary=summary,
            description=description,
            examples=examples,
            headers=headers,
            content_type=content_type,
            traits=traits,
            correlation_id=correlation_id,
            bindings=bindings,
            tags=tags,
            extensions=extensions or {},
        )
        metadata.operations[op_action] = replace(operation, messages=[*(operation.messages or []), message])
        return obj

    return decorator
