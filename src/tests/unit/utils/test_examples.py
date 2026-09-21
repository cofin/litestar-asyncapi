from dataclasses import dataclass
from decimal import Decimal
from random import getstate
from typing import TypedDict
from uuid import UUID

import msgspec
import pytest
from litestar import Litestar
from litestar.typing import FieldDefinition

from litestar_asyncapi import AsyncAPIConfig
from litestar_asyncapi.asyncapi.utils.examples import generate_example, normalize_examples
from litestar_asyncapi.spec import MessageExample
from litestar_asyncapi.spec.base import UNSET


def test_fixed_tuple_example_has_both_positions() -> None:
    example = generate_example(
        FieldDefinition.from_annotation(tuple[int, str]), config=AsyncAPIConfig(create_examples=True)
    )
    assert isinstance(example, list)
    assert len(example) == 2
    assert isinstance(example[0], int)
    assert isinstance(example[1], str)


def test_generation_disabled_distinguishes_null() -> None:
    assert generate_example(FieldDefinition.from_annotation(int), config=AsyncAPIConfig()) is UNSET
    assert (
        generate_example(FieldDefinition.from_annotation(type(None)), config=AsyncAPIConfig(create_examples=True))
        is None
    )


def test_native_model_and_typed_dict_examples() -> None:
    @dataclass
    class Payload:
        value: int

    class Dictionary(TypedDict):
        value: int

    for annotation in (Payload, Dictionary):
        value = generate_example(
            FieldDefinition.from_annotation(annotation), config=AsyncAPIConfig(create_examples=True)
        )
        assert isinstance(value["value"], int)


def test_msgspec_alias_tag_and_tuple_examples_match_wire_types() -> None:
    class Payload(msgspec.Struct, rename="camel", tag="payload"):
        user_name: str
        pair: tuple[int, str]

    example = generate_example(FieldDefinition.from_annotation(Payload), config=AsyncAPIConfig(create_examples=True))
    assert "userName" in example and example["type"] == "payload"
    assert len(example["pair"]) == 2
    assert isinstance(msgspec.convert(example, type=Payload), Payload)


def test_examples_use_application_encoders_and_preserve_metadata() -> None:
    class Custom:
        pass

    app = Litestar([], type_encoders={Custom: lambda value: "encoded"})
    identifier = UUID("00000000-0000-0000-0000-000000000001")
    example = MessageExample(
        payload={"amount": Decimal("1.25"), "id": identifier, "custom": Custom(), "nil": None},
        headers={"h": None},
        name="named",
        summary="summary",
    )
    result = normalize_examples([example, None], app=app)
    assert result[0].to_schema() == {
        "payload": {"amount": "1.25", "id": str(identifier), "custom": "encoded", "nil": None},
        "headers": {"h": None},
        "name": "named",
        "summary": "summary",
    }
    assert result[1].to_schema() == {"payload": None}
    assert normalize_examples([], app=app) == []


def test_generation_does_not_mutate_shared_random_state() -> None:
    from faker import Faker
    from litestar._openapi.schema_generation.examples import ExampleFactory
    from polyfactory.factories.dataclass_factory import DataclassFactory

    @dataclass
    class Payload:
        value: int

    class Registered(DataclassFactory[Payload]):
        __model__ = Payload
        __set_as_default_factory_for_type__ = True

    random_state = getstate()
    native_state = ExampleFactory.__random__.getstate()
    registered_state = Registered.__random__.getstate()
    faker_state = Faker().random.getstate()
    example = generate_example(FieldDefinition.from_annotation(Payload), config=AsyncAPIConfig(create_examples=True))
    assert isinstance(example["value"], int)
    assert getstate() == random_state
    assert ExampleFactory.__random__.getstate() == native_state
    assert Registered.__random__.getstate() == registered_state
    assert Faker().random.getstate() == faker_state


def test_unsupported_generation_warns_and_omits() -> None:
    class RequiredArgument:
        def __init__(self, value: int) -> None:
            self.value = value

    with pytest.warns(UserWarning, match="Omitting automatic AsyncAPI example"):
        assert (
            generate_example(
                FieldDefinition.from_annotation(RequiredArgument), config=AsyncAPIConfig(create_examples=True)
            )
            is UNSET
        )


def test_required_recursive_example_is_omitted_with_warning() -> None:
    @dataclass
    class Required:
        child: "Required"

    with pytest.warns(UserWarning, match="Omitting automatic AsyncAPI example"):
        assert (
            generate_example(FieldDefinition.from_annotation(Required), config=AsyncAPIConfig(create_examples=True))
            is UNSET
        )


def test_factory_configuration_is_rejected_in_clean_break() -> None:
    with pytest.raises(TypeError, match="create_examples must be a bool"):
        AsyncAPIConfig(create_examples={int: object()})


def test_unchecked_direct_constraints_omit_automatic_example() -> None:
    from litestar.params import Parameter

    field = FieldDefinition.from_annotation(str, kwarg_definition=Parameter(min_length=100))
    with pytest.warns(UserWarning, match="direct Parameter constraints"):
        assert generate_example(field, config=AsyncAPIConfig(create_examples=True)) is UNSET


@pytest.mark.parametrize("prefer_alias", [False, True])
def test_generated_decimal_uuid_and_pydantic_aliases(prefer_alias: bool) -> None:
    from litestar.plugins.pydantic import PydanticPlugin
    from pydantic import BaseModel, Field

    from litestar_asyncapi.asyncapi.schema_generation import AsyncAPISchemaGenerator

    class Payload(BaseModel):
        user_name: str = Field(alias="userName", min_length=3)
        amount: Decimal
        identifier: UUID

    app = Litestar([], plugins=[PydanticPlugin(prefer_alias=prefer_alias)])
    example = generate_example(
        FieldDefinition.from_annotation(Payload), config=AsyncAPIConfig(create_examples=True), app=app
    )
    key = "userName" if prefer_alias else "user_name"
    assert key in example
    generator = AsyncAPISchemaGenerator(app)
    generator.generate(Payload)
    assert key in next(iter(generator.components().values()))["properties"]
    assert isinstance(example["amount"], str)
    assert isinstance(example["identifier"], str)
    assert isinstance(
        Payload.model_validate({
            "userName": example[key],
            "amount": example["amount"],
            "identifier": example["identifier"],
        }),
        Payload,
    )
