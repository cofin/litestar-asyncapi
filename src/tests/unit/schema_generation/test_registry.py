import pytest
from litestar.typing import FieldDefinition

from litestar_asyncapi._asyncapi.datastructures import SchemaRegistry
from litestar_asyncapi.spec import Reference, Schema, SchemaType

pytestmark = pytest.mark.anyio


class _ModelA:
    pass


class _ModelB:
    pass


def test_schema_registry_generates_component_names_and_updates_refs() -> None:
    registry = SchemaRegistry()

    fd_a = FieldDefinition.from_annotation(_ModelA)
    fd_b = FieldDefinition.from_annotation(_ModelB)

    a_schema = registry.get_schema_for_field_definition(fd_a)
    b_schema = registry.get_schema_for_field_definition(fd_b)

    a_schema.type = SchemaType.OBJECT
    b_schema.type = SchemaType.OBJECT

    a_ref = registry.get_reference_for_field_definition(fd_a)
    b_ref = registry.get_reference_for_field_definition(fd_b)
    assert isinstance(a_ref, Reference)
    assert isinstance(b_ref, Reference)

    components = registry.generate_components_schemas()
    assert isinstance(components, dict)
    assert any(isinstance(v, Schema) for v in components.values())
    assert a_ref.ref.startswith("#/components/schemas/")
    assert b_ref.ref.startswith("#/components/schemas/")


def test_schema_component_key_override_is_sanitized() -> None:
    from litestar.params import Parameter

    registry = SchemaRegistry()
    field = FieldDefinition.from_annotation(
        dict,
        kwarg_definition=Parameter(schema_component_key="Bad Key!"),
    )

    registry.get_schema_for_field_definition(field)
    ref = registry.get_reference_for_field_definition(field)
    components = registry.generate_components_schemas()

    assert "Bad_Key" in components
    assert isinstance(ref, Reference)
    assert ref.ref == "#/components/schemas/Bad_Key"


def test_schema_component_key_override_rejects_invalid() -> None:
    from litestar.exceptions import ImproperlyConfiguredException
    from litestar.params import Parameter

    registry = SchemaRegistry()
    field = FieldDefinition.from_annotation(
        dict,
        kwarg_definition=Parameter(schema_component_key="!!!"),
    )

    with pytest.raises(ImproperlyConfiguredException):
        registry.get_schema_for_field_definition(field)
