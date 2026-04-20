import pytest
from litestar.exceptions import ImproperlyConfiguredException
from litestar.typing import FieldDefinition

from litestar_asyncapi.asyncapi.datastructures import SchemaRegistry


def test_schema_registry_collision() -> None:
    registry = SchemaRegistry()

    class MyType:
        pass

    class OtherType:
        pass

    field1 = FieldDefinition.from_annotation(MyType)
    field2 = FieldDefinition.from_annotation(OtherType)

    # Force same key by mocking _get_normalized_schema_key if possible,
    # or just use types with same name in different modules if they collide.

    # Actually, we can use two different field definitions for same annotation
    # but different metadata if it affects the key? No, key depends on annotation.

    # Let's mock _get_normalized_schema_key or just use a simpler way.
    # Actually, _get_normalized_schema_key uses FieldDefinition.annotation.

    registry.get_schema_for_field_definition(field1)

    # If we pass a different field definition that results in same key
    # (e.g. same annotation but different metadata that doesn't change key)
    # it should NOT raise unless they are actually different types.

    # Wait, the check is 'if existing_type != field'.
    # FieldDefinition equality includes metadata.

    from dataclasses import replace

    from litestar.params import KwargDefinition

    field1 = replace(field1, kwarg_definition=KwargDefinition(schema_component_key="same"))
    field2 = replace(field2, kwarg_definition=KwargDefinition(schema_component_key="same"))

    registry.get_schema_for_field_definition(field1)

    # This should raise ImproperlyConfiguredException because they have same key but are different
    with pytest.raises(ImproperlyConfiguredException, match="Schema component keys must be unique"):
        registry.get_schema_for_field_definition(field2)


def test_schema_registry_reference_collision() -> None:
    registry = SchemaRegistry()

    class MyType:
        pass

    class OtherType:
        pass

    from dataclasses import replace

    from litestar.params import KwargDefinition

    field1 = replace(
        FieldDefinition.from_annotation(MyType),
        kwarg_definition=KwargDefinition(schema_component_key="same"),
    )
    field2 = replace(
        FieldDefinition.from_annotation(OtherType),
        kwarg_definition=KwargDefinition(schema_component_key="same"),
    )

    registry.get_schema_for_field_definition(field1)

    with pytest.raises(ImproperlyConfiguredException, match="Schema component keys must be unique"):
        registry.get_reference_for_field_definition(field2)


def test_schema_registry_remove_common_prefix() -> None:
    from unittest.mock import patch

    registry = SchemaRegistry()

    class User:
        pass

    field1 = FieldDefinition.from_annotation(User)
    field2 = FieldDefinition.from_annotation(User)

    with patch("litestar_asyncapi.asyncapi.datastructures._get_normalized_schema_key") as mock_key:
        mock_key.side_effect = [("module1", "User"), ("module2", "User"), ("module1", "User"), ("module2", "User")]

        registry.get_schema_for_field_definition(field1)
        registry.get_schema_for_field_definition(field2)

        registry.get_reference_for_field_definition(field1)
        registry.get_reference_for_field_definition(field2)

        components = registry.generate_components_schemas()

        assert "module1_User" in components
        assert "module2_User" in components
        assert "User" not in components  # Collision handled by using full path (minus common prefix)


def test_longest_common_prefix() -> None:
    from litestar_asyncapi.asyncapi.datastructures import _longest_common_prefix

    assert _longest_common_prefix([("a", "b", "c"), ("a", "b", "d")]) == ("a", "b")
    assert _longest_common_prefix([("a", "b"), ("c", "d")]) == ()


def test_normalize_component_key_error() -> None:
    from litestar_asyncapi.asyncapi.datastructures import _normalize_component_key

    with pytest.raises(ImproperlyConfiguredException, match="Invalid schema component key override"):
        _normalize_component_key("!!!")


def test_channel_key() -> None:
    from litestar_asyncapi.asyncapi.generator import _channel_key

    assert _channel_key("/users/{id}") == "/users/{id}"


def test_schema_registry_iter() -> None:
    registry = SchemaRegistry()
    field = FieldDefinition.from_annotation(int)
    registry.get_schema_for_field_definition(field)

    items = list(registry)
    assert len(items) == 1
    assert items[0].field_definition == field
