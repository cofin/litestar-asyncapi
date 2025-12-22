from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, TypeVar

from litestar.exceptions import ImproperlyConfiguredException

from litestar_asyncapi.spec import OperationAction

__all__ = (
    "ASYNCAPI_OPT_KEY",
    "AsyncAPIMessageMetadata",
    "AsyncAPIMetadata",
    "AsyncAPIOperationMetadata",
    "asyncapi_message",
    "asyncapi_operation",
)


ASYNCAPI_OPT_KEY = "asyncapi"


if TYPE_CHECKING:
    from litestar.handlers.base import BaseRouteHandler

T = TypeVar("T")


@dataclass(slots=True)
class AsyncAPIMessageMetadata:
    """Message override metadata attached to a route handler."""

    payload: object | None = None
    name: str | None = None
    title: str | None = None
    summary: str | None = None
    description: str | None = None
    examples: list[Any] | None = None
    headers: object | None = None
    content_type: str | None = None
    traits: list[str] | None = None


@dataclass(slots=True)
class AsyncAPIOperationMetadata:
    """Operation override metadata attached to a route handler."""

    action: OperationAction
    operation_id: str | None = None
    title: str | None = None
    summary: str | None = None
    description: str | None = None
    traits: list[str] | None = None
    message: AsyncAPIMessageMetadata | None = None


@dataclass(slots=True)
class AsyncAPIMetadata:
    """Container for all AsyncAPI metadata attached to a route handler."""

    operations: dict[OperationAction, AsyncAPIOperationMetadata] = field(default_factory=dict)


def _coerce_action(action: OperationAction | str) -> OperationAction:
    if isinstance(action, OperationAction):
        return action
    value = action.strip().lower()
    if value == OperationAction.SEND.value:
        return OperationAction.SEND
    if value == OperationAction.RECEIVE.value:
        return OperationAction.RECEIVE
    msg = f"Invalid action {action!r}. Expected 'send' or 'receive'."
    raise ValueError(msg)


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
    traits: list[str] | None = None,
) -> Callable[[T], T]:
    """Attach AsyncAPI operation metadata to a websocket route handler.

    Returns:
        A decorator that mutates the Litestar route handler metadata in-place.
    """

    op_action = _coerce_action(action)

    def decorator(obj: T) -> T:
        route_handler = _get_route_handler(obj)
        metadata = _get_or_create_metadata(route_handler)

        existing = metadata.operations.get(op_action) or AsyncAPIOperationMetadata(action=op_action)
        if operation_id is not None:
            existing.operation_id = operation_id
        if title is not None:
            existing.title = title
        if summary is not None:
            existing.summary = summary
        if description is not None:
            existing.description = description
        if traits is not None:
            existing.traits = traits
        metadata.operations[op_action] = existing
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
    examples: list[Any] | None = None,
    headers: object | None = None,
    content_type: str | None = None,
    traits: list[str] | None = None,
) -> Callable[[T], T]:
    """Attach AsyncAPI message metadata to a websocket route handler.

    Returns:
        A decorator that mutates the Litestar route handler metadata in-place.
    """

    op_action = _coerce_action(action)

    def decorator(obj: T) -> T:
        route_handler = _get_route_handler(obj)
        metadata = _get_or_create_metadata(route_handler)

        operation = metadata.operations.get(op_action) or AsyncAPIOperationMetadata(action=op_action)
        message = operation.message or AsyncAPIMessageMetadata()

        if payload is not None:
            message.payload = payload
        if name is not None:
            message.name = name
        if title is not None:
            message.title = title
        if summary is not None:
            message.summary = summary
        if description is not None:
            message.description = description
        if examples is not None:
            message.examples = examples
        if headers is not None:
            message.headers = headers
        if content_type is not None:
            message.content_type = content_type
        if traits is not None:
            message.traits = traits

        operation.message = message
        metadata.operations[op_action] = operation
        return obj

    return decorator
