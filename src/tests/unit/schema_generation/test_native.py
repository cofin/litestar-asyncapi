from dataclasses import dataclass

import msgspec
import pytest
from litestar.typing import FieldDefinition

from litestar_asyncapi.asyncapi.schema_generation import AsyncAPISchemaGenerator


@dataclass
class Node:
    children: list["Node"]


class Parent(msgspec.Struct):
    id: int


class Child(Parent, rename="camel", tag="child"):
    user_name: str


def test_recursive_dataclass_succeeds() -> None:
    generator = AsyncAPISchemaGenerator()
    generator.generate(FieldDefinition.from_annotation(Node))
    components = generator.components()
    assert components["Node"]["properties"]["children"]["items"] == {"$ref": "#/components/schemas/Node"}


def test_msgspec_inheritance_alias_and_tag() -> None:
    generator = AsyncAPISchemaGenerator()
    generator.generate(FieldDefinition.from_annotation(Child))
    components = generator.components()
    schema = next(value for name, value in components.items() if name.endswith("Child"))
    assert schema["properties"]["id"]["type"] == "integer"
    assert schema["properties"]["userName"]["type"] == "string"
    assert schema["properties"]["type"]["const"] == "child"


@dataclass
class Left:
    right: "Right | None" = None


@dataclass
class Right:
    left: "Left | None" = None


def test_mutual_recursion_and_finalized_references() -> None:
    generator = AsyncAPISchemaGenerator()
    root = generator.generate(Left)
    components = generator.components()
    assert root == {"$ref": "#/components/schemas/Left"}
    assert "#/components/schemas/Right" in str(components["Left"])
    assert "#/components/schemas/Left" in str(components["Right"])


def test_same_short_names_update_early_references() -> None:
    from dataclasses import make_dataclass

    first = make_dataclass("Model", [("first", int)], namespace={"__module__": "first.models"})
    second = make_dataclass("Model", [("second", str)], namespace={"__module__": "second.models"})
    generator = AsyncAPISchemaGenerator()
    first_ref = generator.generate(first)
    second_ref = generator.generate(second)
    components = generator.components()
    assert isinstance(first_ref, dict) and isinstance(second_ref, dict)
    assert first_ref != second_ref
    assert components[first_ref["$ref"].split("/")[-1]]["properties"]["first"]["type"] == "integer"
    assert components[second_ref["$ref"].split("/")[-1]]["properties"]["second"]["type"] == "string"


def test_nested_and_empty_tuple_cardinality() -> None:

    @dataclass
    class Tuples:
        fixed: tuple[int, str]
        empty: tuple[()]
        variadic: tuple[int, ...]

    generator = AsyncAPISchemaGenerator()
    generator.generate(Tuples)
    properties = next(iter(generator.components().values()))["properties"]
    assert properties["fixed"]["minItems"] == properties["fixed"]["maxItems"] == 2
    assert properties["empty"]["maxItems"] == 0
    assert "maxItems" not in properties["variadic"]
    assert generator.generate(tuple[()])["maxItems"] == 0
    assert "maxItems" not in generator.generate(tuple)
    import importlib

    aliases = vars(importlib.import_module("typing"))
    assert "maxItems" not in generator.generate(aliases["Tuple"])
    assert generator.generate(aliases["Tuple"][()])["maxItems"] == 0


def test_array_like_struct_uses_wire_order_and_accepts_default_tail() -> None:
    class ArrayMessage(msgspec.Struct, array_like=True, tag="message", omit_defaults=True):
        value: int
        label: str = "default"

    generator = AsyncAPISchemaGenerator()
    root = generator.generate(ArrayMessage)
    schemas = generator.components()
    schema = next(iter(schemas.values()))
    assert schema["type"] == "array"
    assert [item.get("const", item.get("type")) for item in schema["items"]] == ["message", "integer", "string"]
    assert schema["minItems"] == 2
    assert "maxItems" not in schema
    assert msgspec.json.decode(msgspec.json.encode(ArrayMessage(1))) == ["message", 1, "default"]
    assert msgspec.json.decode(b'["message",1]', type=ArrayMessage) == ArrayMessage(1)
    assert msgspec.json.decode(b'["message",1,"x",99]', type=ArrayMessage) == ArrayMessage(1, "x")
    assert root


def test_array_like_struct_can_forbid_extra_items() -> None:
    class StrictArray(msgspec.Struct, array_like=True, forbid_unknown_fields=True):
        value: int

    generator = AsyncAPISchemaGenerator()
    generator.generate(StrictArray)
    assert next(iter(generator.components().values()))["maxItems"] == 1
    with pytest.raises(msgspec.ValidationError):
        msgspec.json.decode(b"[1,2]", type=StrictArray)


def test_pydantic_aliases_and_constraints() -> None:
    from litestar import Litestar
    from litestar.plugins.pydantic import PydanticPlugin
    from pydantic import BaseModel, Field

    class Model(BaseModel):
        user_name: str = Field(alias="userName", min_length=2)
        count: int = Field(gt=0)

    generator = AsyncAPISchemaGenerator(Litestar([], plugins=[PydanticPlugin(prefer_alias=True)]))
    generator.generate(Model)
    props = next(iter(generator.components().values()))["properties"]
    assert props["userName"]["minLength"] == 2
    assert props["count"]["exclusiveMinimum"] == 0


def test_attrs_and_typed_dict_models() -> None:
    import attrs
    from typing_extensions import TypedDict

    @attrs.define
    class AttrsModel:
        value: int

    class TypedModel(TypedDict):
        value: str

    generator = AsyncAPISchemaGenerator()
    generator.generate(AttrsModel)
    generator.generate(TypedModel)
    components = generator.components()
    assert {value["properties"]["value"]["type"] for value in components.values()} == {"integer", "string"}
    assert all(value["required"] == ["value"] for value in components.values())


def test_native_constraints_containers_and_literals() -> None:
    from typing import Literal

    from litestar.params import Parameter

    generator = AsyncAPISchemaGenerator()
    schema = generator.generate(
        FieldDefinition.from_annotation(str, kwarg_definition=Parameter(min_length=2, max_length=5))
    )
    assert schema["minLength"] == 2 and schema["maxLength"] == 5
    assert generator.generate(list[int])["items"] == {"type": "integer"}
    assert generator.generate(dict[str, int])["additionalProperties"] == {"type": "integer"}
    assert generator.generate(Literal[1])["const"] == 1
    assert "null" in str(generator.generate(int | None))


def test_application_plugin_works_with_openapi_disabled_and_preserves_literals() -> None:
    from litestar import Litestar
    from litestar.openapi.spec import Schema
    from litestar.plugins import OpenAPISchemaPlugin

    class Custom:
        pass

    class CustomPlugin(OpenAPISchemaPlugin):
        def is_plugin_supported_field(self, field_definition):
            return field_definition.annotation is Custom

        def to_openapi_schema(self, field_definition, schema_creator):
            return Schema(
                default={"nested": {"value": None}}, examples=[{"value": None}], prefix_items=[Schema(type="integer")]
            )

    app = Litestar([], openapi_config=None, plugins=[CustomPlugin()], signature_namespace={"Payload": Custom})
    generator = AsyncAPISchemaGenerator(app)
    assert generator.generate("Payload") == {
        "default": {"nested": {"value": None}},
        "examples": [{"value": None}],
        "items": [{"type": "integer"}],
    }


def test_generation_registry_is_independent_from_application_openapi() -> None:
    from litestar import Litestar

    app = Litestar([])
    before = app.openapi_schema.to_schema()
    first = AsyncAPISchemaGenerator(app)
    first.generate(Node)
    assert first.components()
    assert AsyncAPISchemaGenerator(app).components() == {}
    assert app.openapi_schema.to_schema() == before


def test_unsupported_native_output_has_payload_and_handler_context() -> None:
    from litestar import Litestar
    from litestar.exceptions import ImproperlyConfiguredException
    from litestar.openapi.spec import Schema
    from litestar.plugins import OpenAPISchemaPlugin

    class Unsupported:
        pass

    class CustomPlugin(OpenAPISchemaPlugin):
        def is_plugin_supported_field(self, field_definition):
            return field_definition.annotation is Unsupported

        def to_openapi_schema(self, field_definition, schema_creator):
            return Schema(min_contains=2)

    generator = AsyncAPISchemaGenerator(Litestar([], plugins=[CustomPlugin()]))
    with pytest.raises(ImproperlyConfiguredException, match=r"Unsupported.*handler.*minContains"):
        generator.generate(Unsupported, provenance="handler /events")


def test_unresolved_namespace_has_payload_and_handler_context() -> None:
    from litestar.exceptions import ImproperlyConfiguredException

    with pytest.raises(ImproperlyConfiguredException, match=r"MissingPayload.*events"):
        AsyncAPISchemaGenerator().generate("MissingPayload", provenance="events")


def test_explicit_field_default_null_differs_from_absent_default() -> None:
    @dataclass
    class Nullable:
        required: str | None
        optional: str | None = None

    generator = AsyncAPISchemaGenerator()
    generator.generate(Nullable)
    properties = next(iter(generator.components().values()))["properties"]
    assert "default" not in properties["required"]
    assert properties["optional"]["default"] is None


def test_array_like_required_position_after_default() -> None:
    class Ordered(msgspec.Struct, array_like=True, kw_only=True):
        optional: int = 1
        required: str

    generator = AsyncAPISchemaGenerator()
    generator.generate(Ordered)
    assert next(iter(generator.components().values()))["minItems"] == 2
    assert msgspec.json.decode(msgspec.json.encode(Ordered(required="x"))) == [1, "x"]
    with pytest.raises(msgspec.ValidationError):
        msgspec.json.decode(b"[1]", type=Ordered)


def test_application_tuple_and_struct_plugins_override_native_shapes() -> None:
    from litestar import Litestar
    from litestar.openapi.spec import Schema
    from litestar.plugins import OpenAPISchemaPlugin

    class ArrayMessage(msgspec.Struct, array_like=True):
        value: int

    class OverridePlugin(OpenAPISchemaPlugin):
        def is_plugin_supported_field(self, field_definition):
            return field_definition.annotation in (tuple[int, str], ArrayMessage)

        def to_openapi_schema(self, field_definition, schema_creator):
            return Schema(type="string", pattern="custom")

    generator = AsyncAPISchemaGenerator(Litestar([], plugins=[OverridePlugin()]))
    for annotation in (tuple[int, str], ArrayMessage):
        assert generator.generate(annotation) == {"type": "string", "pattern": "custom"}
    assert generator.components() == {}


def test_unresolved_nested_local_forward_reference_has_context() -> None:
    from litestar.exceptions import ImproperlyConfiguredException

    @dataclass
    class LocalNode:
        value: "LocalNode"

    with pytest.raises(ImproperlyConfiguredException, match=r"LocalNode.*local handler"):
        AsyncAPISchemaGenerator().generate(LocalNode, provenance="local handler")


def test_tuple_bounds_intersect_annotation_constraints() -> None:
    from litestar.params import Parameter

    field = FieldDefinition.from_annotation(tuple[int, str], kwarg_definition=Parameter(min_items=3, max_items=4))
    schema = AsyncAPISchemaGenerator().generate(field)
    assert schema["minItems"] == 3
    assert schema["maxItems"] == 2


def test_tuple_zero_maximum_is_not_dropped() -> None:
    from litestar.params import Parameter

    field = FieldDefinition.from_annotation(tuple[int], kwarg_definition=Parameter(max_items=0))
    schema = AsyncAPISchemaGenerator().generate(field)
    assert schema["minItems"] == 1
    assert schema["maxItems"] == 0


def test_native_projection_honors_excluded_fields() -> None:
    from dataclasses import dataclass

    from litestar.openapi.spec import Schema

    from litestar_asyncapi._compat import normalize_native_schema

    @dataclass
    class FilteredSchema(Schema):
        internal: str = "private"

        @property
        def _exclude_fields(self):
            return {"internal"}

    assert normalize_native_schema(FilteredSchema(default={"value": None})) == {"default": {"value": None}}


def test_explicit_multiformat_bypasses_native_dialect_conversion() -> None:
    from litestar_asyncapi.spec import MultiFormatSchema

    schema = MultiFormatSchema("application/schema+json;version=draft-2020-12", {"unevaluatedProperties": False})
    assert AsyncAPISchemaGenerator().generate(schema) == schema.to_schema()


@pytest.mark.parametrize("keyword", ["const", "default"])
def test_explicit_schema_extra_null_preserves_presence(keyword: str) -> None:
    from typing import Any

    from litestar.params import Parameter

    field = FieldDefinition.from_annotation(Any, kwarg_definition=Parameter(schema_extra={keyword: None}))
    assert AsyncAPISchemaGenerator().generate(field) == {keyword: None}


def test_mixed_literal_types_generate_listener_and_decorator_documents() -> None:
    from typing import Any, Literal

    from litestar import Litestar, websocket, websocket_listener

    from litestar_asyncapi import AsyncAPIConfig, asyncapi_message, asyncapi_operation
    from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator

    @websocket_listener("/literal")
    async def listener(data: Literal[1] | None) -> None:
        return None

    @asyncapi_operation(action="receive")
    @asyncapi_message(action="receive", payload=Literal[1] | None)
    @websocket("/decorated")
    async def decorated(socket: Any) -> None:
        return None

    app = Litestar([listener, decorated])
    document = AsyncAPIGenerator(app=app, config=AsyncAPIConfig()).build_schema()
    for channel in document["channels"].values():
        payload = next(iter(channel["messages"].values()))["payload"]
        assert set(payload["type"]) == {"integer", "null"}
