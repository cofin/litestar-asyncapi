from dataclasses import dataclass
from typing import TypedDict

import pytest
from litestar.typing import FieldDefinition

from litestar_asyncapi import AsyncAPIConfig
from litestar_asyncapi.asyncapi.utils.examples import generate_example

pytestmark = pytest.mark.anyio


def test_generate_example_for_dataclass() -> None:
    @dataclass
    class Payload:
        value: int

    field = FieldDefinition.from_annotation(Payload)
    config = AsyncAPIConfig(create_examples=True, random_seed=1)
    example = generate_example(field, config=config)

    assert isinstance(example, dict)
    assert "value" in example


def test_generate_example_for_typed_dict() -> None:
    class Payload(TypedDict):
        value: int

    field = FieldDefinition.from_annotation(Payload)
    config = AsyncAPIConfig(create_examples=True, random_seed=1)
    example = generate_example(field, config=config)

    assert isinstance(example, dict)
    assert "value" in example


def test_generate_example_for_primitives_and_containers() -> None:
    config = AsyncAPIConfig(create_examples=True)

    assert generate_example(FieldDefinition.from_annotation(int), config=config) == 0
    assert generate_example(FieldDefinition.from_annotation(str), config=config) == "string"
    assert generate_example(FieldDefinition.from_annotation(bool), config=config) is False
    assert generate_example(FieldDefinition.from_annotation(float), config=config) == pytest.approx(0.0)
    assert generate_example(FieldDefinition.from_annotation(bytes), config=config) == "bytes"
    assert generate_example(FieldDefinition.from_annotation(list[int]), config=config) == [0]
    assert generate_example(FieldDefinition.from_annotation(dict[str, int]), config=config) == {"key": 0}
    assert generate_example(FieldDefinition.from_annotation(type(None)), config=config) is None


def test_generate_example_for_optional_and_enum() -> None:
    from enum import Enum

    class ExampleEnum(str, Enum):
        FIRST = "first"
        SECOND = "second"

    config = AsyncAPIConfig(create_examples=True)

    assert generate_example(FieldDefinition.from_annotation(str | None), config=config) == "string"
    assert generate_example(FieldDefinition.from_annotation(ExampleEnum), config=config) == "first"


def test_generate_example_disabled_returns_none() -> None:
    assert generate_example(FieldDefinition.from_annotation(int), config=AsyncAPIConfig()) is None


def test_generate_example_with_factory_instance() -> None:
    class ExampleFactory:
        def build(self) -> dict[str, int]:
            return {"value": 5}

    config = AsyncAPIConfig(create_examples=ExampleFactory())
    assert generate_example(FieldDefinition.from_annotation(int), config=config) == {"value": 5}


def test_generate_example_with_factory_mapping() -> None:
    @dataclass
    class BasePayload:
        value: int

    @dataclass
    class SubPayload(BasePayload):
        extra: int

    from polyfactory.factories.dataclass_factory import DataclassFactory

    config = AsyncAPIConfig(create_examples={BasePayload: DataclassFactory}, random_seed=1)
    example = generate_example(FieldDefinition.from_annotation(SubPayload), config=config)

    assert isinstance(example, dict)
    assert "extra" in example


def test_generate_example_with_exact_factory_mapping() -> None:
    @dataclass
    class Payload:
        value: int

    from polyfactory.factories.dataclass_factory import DataclassFactory

    config = AsyncAPIConfig(create_examples={Payload: DataclassFactory}, random_seed=1)
    example = generate_example(FieldDefinition.from_annotation(Payload), config=config)

    assert isinstance(example, dict)
    assert "value" in example


def test_generate_example_with_none_factory_mapping() -> None:
    @dataclass
    class Payload:
        value: int

    config = AsyncAPIConfig(create_examples={Payload: None})
    assert generate_example(FieldDefinition.from_annotation(Payload), config=config) is None


def test_generate_example_with_failing_factory() -> None:
    class FailingFactory:
        def create_factory(self, _annotation: object) -> "FailingFactory":
            raise ValueError

    config = AsyncAPIConfig(create_examples=FailingFactory())
    assert generate_example(FieldDefinition.from_annotation(int), config=config) == 0


def test_generate_example_with_failing_build() -> None:
    class FailingFactory:
        def build(self) -> dict[str, int]:
            raise ValueError

    config = AsyncAPIConfig(create_examples=FailingFactory())
    assert generate_example(FieldDefinition.from_annotation(int), config=config) == 0


def test_generate_example_normalizes_model_dump() -> None:
    class WithModelDump:
        def model_dump(self) -> dict[str, int]:
            return {"value": 10}

    class ExampleFactory:
        def build(self) -> WithModelDump:
            return WithModelDump()

    config = AsyncAPIConfig(create_examples=ExampleFactory())
    assert generate_example(FieldDefinition.from_annotation(int), config=config) == {"value": 10}


def test_generate_example_normalizes_dict_method() -> None:
    class WithDict:
        def dict(self) -> dict[str, int]:
            return {"value": 12}

    class ExampleFactory:
        def build(self) -> WithDict:
            return WithDict()

    config = AsyncAPIConfig(create_examples=ExampleFactory())
    assert generate_example(FieldDefinition.from_annotation(int), config=config) == {"value": 12}


def test_generate_example_for_msgspec_struct() -> None:
    import msgspec

    class Payload(msgspec.Struct):
        value: int

    config = AsyncAPIConfig(create_examples=True, random_seed=1)
    example = generate_example(FieldDefinition.from_annotation(Payload), config=config)

    assert isinstance(example, dict)
    assert "value" in example


def test_generate_example_for_pydantic_model() -> None:
    import pydantic

    class Payload(pydantic.BaseModel):
        value: int

    config = AsyncAPIConfig(create_examples=True, random_seed=1)
    example = generate_example(FieldDefinition.from_annotation(Payload), config=config)

    assert isinstance(example, dict)
    assert "value" in example


def test_generate_example_uses_kwarg_defaults() -> None:
    from dataclasses import replace

    from litestar.params import KwargDefinition
    from litestar.types import Empty

    base_field = FieldDefinition.from_annotation(int)
    with_default = replace(base_field, kwarg_definition=KwargDefinition(default=12))
    with_const = replace(base_field, kwarg_definition=KwargDefinition(default=15, const=True))
    with_enum = replace(base_field, kwarg_definition=KwargDefinition(enum=[1, 2, 3]))
    with_empty = replace(base_field, kwarg_definition=KwargDefinition(default=Empty))

    config = AsyncAPIConfig(create_examples=True)
    assert generate_example(with_default, config=config) == 12
    assert generate_example(with_const, config=config) == 15
    assert generate_example(with_enum, config=config) in {1, 2, 3}
    assert generate_example(with_empty, config=config) == 0
