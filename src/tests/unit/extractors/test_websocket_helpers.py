import pytest
from litestar.types.builtin_types import NoneType
from litestar.typing import FieldDefinition

from litestar_asyncapi._asyncapi.extractors import websocket as websocket_extractor
from litestar_asyncapi.spec import Reference, Schema, SchemaType

pytestmark = pytest.mark.anyio


def test_is_none_return_type() -> None:
    assert websocket_extractor._is_none_return_type(FieldDefinition.from_annotation(NoneType)) is True
    assert websocket_extractor._is_none_return_type(FieldDefinition.from_annotation(int)) is False


def test_infer_content_type_returns_none_for_untyped_schema() -> None:
    assert websocket_extractor._infer_content_type(Schema()) is None


def test_infer_content_type_detects_json_from_ref_and_object() -> None:
    assert websocket_extractor._infer_content_type(Reference(ref="#/components/schemas/User")) == "application/json"
    payload = Schema(type=SchemaType.OBJECT, properties={"id": Schema(type=SchemaType.INTEGER)})
    assert websocket_extractor._infer_content_type(payload) == "application/json"


def test_infer_content_type_detects_json_from_array() -> None:
    assert websocket_extractor._infer_content_type(Schema(type=SchemaType.ARRAY)) == "application/json"
