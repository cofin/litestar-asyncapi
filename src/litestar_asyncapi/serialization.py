from typing import TYPE_CHECKING, Any, cast

from litestar.serialization import decode_json, encode_json, get_serializer

from litestar_asyncapi.spec import AsyncAPI

if TYPE_CHECKING:
    from litestar.types import TypeEncodersMap

__all__ = ("normalize_document", "normalize_value")


def normalize_value(value: Any, type_encoders: "TypeEncodersMap | None" = None) -> Any:
    """Normalize arbitrary values through Litestar's JSON serializer and application encoders."""
    return decode_json(encode_json(value, serializer=get_serializer(type_encoders)))


def normalize_document(
    document: AsyncAPI | dict[str, Any], type_encoders: "TypeEncodersMap | None" = None
) -> dict[str, Any]:
    """Produce independent JSON-compatible values through Litestar's application encoders."""
    value = document.to_schema() if isinstance(document, AsyncAPI) else document
    return cast("dict[str, Any]", normalize_value(value, type_encoders))
