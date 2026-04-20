from dataclasses import asdict, is_dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, get_args, get_origin

from litestar.params import KwargDefinition
from litestar.types import Empty
from litestar.typing import FieldDefinition

from litestar.utils.predicates import is_optional_union, is_union
from litestar.utils.typing import make_non_optional_union

if TYPE_CHECKING:
    from litestar_asyncapi import AsyncAPIConfig

__all__ = ("generate_example",)


def generate_example(field_definition: FieldDefinition, *, config: "AsyncAPIConfig") -> Any | None:
    """Generate an example value for a field definition.

    Args:
        field_definition: Field definition to generate an example for.
        config: AsyncAPI configuration controlling example generation.

    Returns:
        An example value or ``None`` if no example can be generated.
    """

    if not config.create_examples:
        return None

    kwarg_definition = field_definition.kwarg_definition
    if isinstance(kwarg_definition, KwargDefinition):
        if kwarg_definition.const and kwarg_definition.default is not Empty:
            return kwarg_definition.default
        if kwarg_definition.default is not Empty:
            return kwarg_definition.default
        if kwarg_definition.enum:
            return next(iter(kwarg_definition.enum))

    annotation = field_definition.raw or field_definition.annotation
    if annotation is None:
        return None

    example = _example_from_factory(annotation, config=config)
    if example is not None:
        return _normalize_example_value(example)

    return _basic_example_for_annotation(annotation)


def _example_from_factory(annotation: Any, *, config: "AsyncAPIConfig") -> Any | None:
    factory_config = config.create_examples
    if isinstance(factory_config, dict):
        for key, factory in factory_config.items():
            if annotation is key:
                return _build_with_factory(factory, annotation, config=config)
            if isinstance(annotation, type) and isinstance(key, type) and issubclass(annotation, key):
                return _build_with_factory(factory, annotation, config=config)
        return None

    if factory_config is True:
        factory = _default_factory_for_model(annotation)
        if factory is None:
            return None
        return _build_with_factory(factory, annotation, config=config)

    return _build_with_factory(factory_config, annotation, config=config)


def _build_with_factory(factory: Any, annotation: Any, *, config: "AsyncAPIConfig") -> Any | None:
    if factory is None or factory is False:
        return None

    if hasattr(factory, "create_factory"):
        try:
            factory = factory.create_factory(annotation)
        except (TypeError, ValueError):
            return None

    if hasattr(factory, "seed_random") and config.random_seed is not None:
        factory.seed_random(config.random_seed)

    if hasattr(factory, "build"):
        try:
            return factory.build()
        except (TypeError, ValueError):
            return None

    return None


def _default_factory_for_model(annotation: Any) -> Any | None:
    dataclass_factory = None
    typed_dict_factory = None
    msgspec_factory = None
    pydantic_factory = None

    try:
        from polyfactory.factories.dataclass_factory import DataclassFactory

        dataclass_factory = DataclassFactory
    except ImportError:
        dataclass_factory = None

    try:
        from polyfactory.factories.typed_dict_factory import TypedDictFactory

        typed_dict_factory = TypedDictFactory
    except ImportError:
        typed_dict_factory = None

    try:
        from polyfactory.factories.msgspec_factory import MsgspecFactory

        msgspec_factory = MsgspecFactory
    except ImportError:
        msgspec_factory = None

    try:
        from polyfactory.factories.pydantic_factory import ModelFactory

        pydantic_factory = ModelFactory
    except ImportError:
        pydantic_factory = None

    if dataclass_factory is not None and is_dataclass(annotation):
        return dataclass_factory

    if typed_dict_factory is not None and _is_typed_dict(annotation):
        return typed_dict_factory

    if msgspec_factory is not None:
        try:
            import msgspec
        except ImportError:
            msgspec = None  # type: ignore[assignment]

        if msgspec is not None and isinstance(annotation, type) and issubclass(annotation, msgspec.Struct):
            return msgspec_factory

    if pydantic_factory is not None:
        try:
            import pydantic
        except ImportError:
            pydantic = None  # type: ignore[assignment]

        pydantic_base_model = getattr(pydantic, "BaseModel", None) if pydantic is not None else None

        if (
            pydantic_base_model is not None
            and isinstance(annotation, type)
            and issubclass(annotation, pydantic_base_model)
        ):
            return pydantic_factory

    return None


def _basic_example_for_annotation(annotation: Any) -> Any | None:
    if is_optional_union(annotation):
        non_none = make_non_optional_union(annotation)
        return _basic_example_for_annotation(non_none)

    if is_union(annotation):
        union_args = get_args(annotation)
        return _basic_example_for_annotation(union_args[0])

    origin = get_origin(annotation)
    if origin in {list, tuple, set}:
        args = get_args(annotation)
        item = _basic_example_for_annotation(args[0]) if args else None
        return [item]

    if origin is dict:
        args = get_args(annotation)
        value = _basic_example_for_annotation(args[1]) if len(args) > 1 else None
        return {"key": value}

    if isinstance(annotation, type) and issubclass(annotation, Enum):
        members = list(annotation)
        return members[0].value if members else None

    if annotation is str:
        return "string"
    if annotation is int:
        return 0
    if annotation is float:
        return 0.0
    if annotation is bool:
        return False
    if annotation is bytes:
        return "bytes"

    if annotation is type(None):
        return None

    if origin is None and isinstance(annotation, type) and is_dataclass(annotation):
        return None

    return None


def _normalize_example_value(value: Any) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        return asdict(value)

    if isinstance(value, type):
        return value

    if hasattr(value, "model_dump"):
        return value.model_dump()

    if hasattr(value, "dict"):
        return value.dict()

    try:
        import msgspec
    except ImportError:
        msgspec = None  # type: ignore[assignment]

    if msgspec is not None and isinstance(value, msgspec.Struct):
        return msgspec.to_builtins(value)

    return value


def _is_typed_dict(annotation: Any) -> bool:
    return isinstance(annotation, type) and issubclass(annotation, dict) and hasattr(annotation, "__total__")
