import pytest
from litestar.exceptions import ImproperlyConfiguredException

from litestar_asyncapi.asyncapi.schema_generation.dialect import to_asyncapi_schema


def test_tuple_dialect_conversion_preserves_explicit_length() -> None:
    source = {
        "type": "array",
        "prefixItems": [{"type": "string"}, {"type": "integer"}],
        "items": False,
        "minItems": 2,
        "maxItems": 2,
    }
    assert to_asyncapi_schema(source) == {
        "type": "array",
        "items": [{"type": "string"}, {"type": "integer"}],
        "additionalItems": False,
        "minItems": 2,
        "maxItems": 2,
    }


def test_prefix_items_does_not_infer_cardinality() -> None:
    assert to_asyncapi_schema({"prefixItems": [{"type": "string"}]}) == {"items": [{"type": "string"}]}
    assert to_asyncapi_schema({"prefixItems": [], "items": False}) == {"items": False}
    assert to_asyncapi_schema({"prefixItems": []}) == {}


def test_only_schema_positions_are_converted() -> None:
    literal = {"prefixItems": [None], "$defs": {"X": False}, "$ref": "#/$defs/X", "unevaluatedProperties": None}
    source = {
        "const": literal,
        "default": literal,
        "examples": [literal],
        "x-literal": literal,
        "properties": {"example": {"prefixItems": [False]}, "$defs": {"type": "string"}},
    }
    converted = to_asyncapi_schema(source)
    assert isinstance(converted, dict)
    for key in ("const", "default", "x-literal"):
        assert converted[key] == literal
        assert converted[key] is not literal
    assert converted["examples"] == [literal]
    assert converted["properties"]["example"] == {"items": [False]}
    assert source["properties"]["example"] == {"prefixItems": [False]}
    assert to_asyncapi_schema(False) is False
    assert to_asyncapi_schema(True) is True


def test_recursive_definition_references_and_pointer_tokens() -> None:
    source = {
        "$defs": {"a/b~c": {"properties": {"next": {"$ref": "#/$defs/a~1b~0c"}}}},
        "properties": {"$defs": {"type": "string"}, "literal": {"$ref": "#/properties/$defs"}},
        "allOf": [{"$ref": "#/$defs/a~1b~0c"}, {"$ref": "https://example.com/schema#/$defs/X"}],
    }
    converted = to_asyncapi_schema(source)
    assert isinstance(converted, dict)
    assert converted["definitions"]["a/b~c"]["properties"]["next"]["$ref"] == "#/definitions/a~1b~0c"
    assert converted["allOf"][0]["$ref"] == "#/definitions/a~1b~0c"
    assert converted["allOf"][1]["$ref"] == "https://example.com/schema#/$defs/X"
    assert converted["properties"]["literal"]["$ref"] == "#/properties/$defs"


def test_reference_siblings_keep_validation_constraints() -> None:
    assert to_asyncapi_schema({"$ref": "#/definitions/X", "maxLength": 3}) == {
        "maxLength": 3,
        "allOf": [{"$ref": "#/definitions/X"}],
    }


def test_dependencies_overlap_without_overwrite() -> None:
    converted = to_asyncapi_schema({
        "dependencies": {"name": ["existing"]},
        "dependentRequired": {"name": ["required"], "other": ["extra"]},
        "dependentSchemas": {"name": {"properties": {"tuple": {"prefixItems": [True]}}}},
    })
    assert converted == {
        "dependencies": {
            "name": {
                "allOf": [
                    {"required": ["existing"]},
                    {"required": ["required"]},
                    {"properties": {"tuple": {"items": [True]}}},
                ]
            },
            "other": ["extra"],
        }
    }


def test_discriminator_branches_and_null_survive() -> None:
    branch = {"type": "object", "properties": {"tag": {"const": "one"}}, "required": ["tag"]}
    assert to_asyncapi_schema({
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "oneOf": [branch, {"const": None}],
        "discriminator": {"propertyName": "tag"},
    }) == {"oneOf": [branch, {"const": None}]}
    assert to_asyncapi_schema({"discriminator": "tag"}) == {"discriminator": "tag"}


@pytest.mark.parametrize(
    "keyword",
    [
        "unevaluatedItems",
        "unevaluatedProperties",
        "$dynamicRef",
        "$dynamicAnchor",
        "$recursiveRef",
        "$recursiveAnchor",
        "$anchor",
        "$vocabulary",
        "minContains",
        "maxContains",
        "contentSchema",
        "nullable",
    ],
)
def test_unsupported_semantics_report_schema_path(keyword: str) -> None:
    with pytest.raises(ImproperlyConfiguredException, match="properties/a~1b/"):
        to_asyncapi_schema({"properties": {"a/b": {keyword: False}}})


def test_invalid_schema_shapes_fail_instead_of_weakening() -> None:
    for schema in [
        {"prefixItems": "invalid"},
        {"items": None},
        {"$defs": {}, "definitions": {}},
        {"prefixItems": [True], "items": True, "additionalItems": False},
        {"$ref": "#anchor"},
        {"$schema": "https://example.com/custom"},
    ]:
        with pytest.raises(ImproperlyConfiguredException):
            to_asyncapi_schema(schema)


def test_definition_references_escape_uri_tokens() -> None:
    source = {"$defs": {"%2F #": {"type": "string"}}, "allOf": [{"$ref": "#/$defs/%252F%20%23"}]}
    assert to_asyncapi_schema(source) == {
        "definitions": {"%2F #": {"type": "string"}},
        "allOf": [{"$ref": "#/definitions/%252F%20%23"}],
    }


def test_nested_resource_ids_are_rejected() -> None:
    with pytest.raises(ImproperlyConfiguredException, match="nested \\$id changes reference scope"):
        to_asyncapi_schema({"$defs": {"X": {"$id": "other.json", "$ref": "#/$defs/X"}}})


def test_declared_draft07_preserves_reference_sibling_semantics() -> None:
    source = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "definitions": {"value": {"type": "integer"}},
        "$ref": "#/definitions/value",
        "type": "string",
    }
    assert to_asyncapi_schema(source) == {
        "definitions": {"value": {"type": "integer"}},
        "$ref": "#/definitions/value",
        "type": "string",
    }


def test_declared_legacy_does_not_reinterpret_modern_annotations() -> None:
    with pytest.raises(ImproperlyConfiguredException, match="cannot reinterpret modern keyword prefixItems"):
        to_asyncapi_schema({"$schema": "http://json-schema.org/draft-07/schema#", "prefixItems": [False]})
    with pytest.raises(ImproperlyConfiguredException, match="mixed schema dialects"):
        to_asyncapi_schema({"properties": {"nested": {"$schema": "http://json-schema.org/draft-07/schema#"}}})


def test_declared_2019_dialect_is_not_reinterpreted_as_2020() -> None:
    with pytest.raises(ImproperlyConfiguredException, match="unsupported schema dialect"):
        to_asyncapi_schema({"$schema": "https://json-schema.org/draft/2019-09/schema", "prefixItems": [False]})
