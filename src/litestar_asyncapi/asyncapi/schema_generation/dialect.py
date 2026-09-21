from collections.abc import Mapping
from copy import deepcopy
from typing import Any, NoReturn
from urllib.parse import quote, unquote

from litestar.exceptions import ImproperlyConfiguredException

__all__ = ("to_asyncapi_schema",)

_SCHEMA_MAPS = {"properties", "patternProperties", "definitions", "$defs"}
_SCHEMA_LISTS = {"allOf", "anyOf", "oneOf"}
_SCHEMA_VALUES = {"additionalProperties", "additionalItems", "contains", "propertyNames", "not", "if", "then", "else"}
_UNSUPPORTED = {
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
}


def _pointer(path: tuple[str, ...]) -> str:
    pointer = "".join("/" + token.replace("~", "~0").replace("/", "~1") for token in path)
    return "#" + quote(pointer, safe="/~!$&'()*+,;=:@?")


def _fail(path: tuple[str, ...], message: str) -> NoReturn:
    detail = f"Cannot export AsyncAPI Draft07 schema at {_pointer(path)}: {message}"
    raise ImproperlyConfiguredException(detail)


class _Converter:
    """Track schema positions and moved reference targets during export."""

    __slots__ = ("legacy", "locations", "references")

    def __init__(self, *, legacy: bool = False) -> None:
        self.legacy = legacy
        self.locations: dict[tuple[str, ...], tuple[str, ...]] = {}
        self.references: list[dict[str, Any]] = []

    def convert(self, schema: Any, source: tuple[str, ...], target: tuple[str, ...]) -> dict[str, Any] | bool:
        self.locations[source] = target
        if isinstance(schema, bool):
            return schema
        if not isinstance(schema, Mapping):
            _fail(source, "expected a schema mapping or boolean")
        if "prefixItems" in schema and "additionalItems" in schema:
            _fail((*source, "additionalItems"), "additionalItems cannot accompany modern prefixItems")
        result: dict[str, Any] = {}
        for key, item in schema.items():
            current = (*source, key)
            if key == "$id" and source:
                _fail(current, "nested $id changes reference scope and is unsupported")
            if self.legacy and key in {"$defs", "prefixItems", "dependentRequired", "dependentSchemas"}:
                _fail(current, f"cannot reinterpret modern keyword {key} in declared Draft07 schema")
            if key in _UNSUPPORTED:
                _fail(current, f"unsupported keyword {key}")
            if key == "$schema":
                declared_legacy = item in {
                    "http://json-schema.org/draft-07/schema#",
                    "http://json-schema.org/draft-07/schema",
                }
                if declared_legacy != self.legacy:
                    _fail(current, "mixed schema dialects are unsupported")
                if item not in {
                    "http://json-schema.org/draft-07/schema#",
                    "http://json-schema.org/draft-07/schema",
                    "https://json-schema.org/draft/2020-12/schema",
                }:
                    _fail(current, f"unsupported schema dialect {item!r}")
                continue
            if key == "discriminator" and isinstance(item, Mapping):
                continue
            if key in {"dependentRequired", "dependentSchemas", "dependencies"}:
                continue
            if key == "$ref":
                if not isinstance(item, str):
                    _fail(current, "$ref must be a string")
                if item.startswith("#") and not item.startswith("#/") and item != "#":
                    _fail(current, "named anchor references are unsupported")
                result[key] = item
                continue
            self.keyword(schema, key, item, source, target, result=result)
        self.dependencies(schema, source, target, result)
        if "$ref" in result:
            if len(result) > 1 and not self.legacy:
                reference = {"$ref": result.pop("$ref")}
                result.setdefault("allOf", []).append(reference)
                self.references.append(reference)
            else:
                self.references.append(result)
        return result

    def dependencies(
        self, schema: Mapping[str, Any], source: tuple[str, ...], target: tuple[str, ...], result: dict[str, Any]
    ) -> None:
        dependencies: dict[str, list[tuple[str, Any]]] = {}
        for keyword in ("dependencies", "dependentRequired", "dependentSchemas"):
            entries = schema.get(keyword, {})
            if not isinstance(entries, Mapping):
                _fail((*source, keyword), f"{keyword} must be a mapping")
            for name, entry in entries.items():
                if keyword == "dependentRequired" and not isinstance(entry, list):
                    _fail((*source, keyword, name), "dependentRequired values must be string arrays")
                if isinstance(entry, list) and not all(isinstance(item, str) for item in entry):
                    _fail((*source, keyword, name), "dependency arrays must contain strings")
                if keyword == "dependentSchemas" and isinstance(entry, list):
                    _fail((*source, keyword, name), "dependentSchemas values must be schemas")
                dependencies.setdefault(name, []).append((keyword, entry))
        if dependencies:
            result["dependencies"] = {}
            for name, entries in dependencies.items():
                combined = len(entries) > 1
                converted: list[Any] = []
                for index, (keyword, entry) in enumerate(entries):
                    destination = (*target, "dependencies", name)
                    if combined:
                        destination = (*destination, "allOf", str(index))
                    if isinstance(entry, list):
                        converted.append({"required": deepcopy(entry)} if combined else deepcopy(entry))
                    else:
                        converted.append(self.convert(entry, (*source, keyword, name), destination))
                result["dependencies"][name] = {"allOf": converted} if combined else converted[0]

    def keyword(
        self,
        schema: Mapping[str, Any],
        key: str,
        item: Any,
        source: tuple[str, ...],
        target: tuple[str, ...],
        *,
        result: dict[str, Any],
    ) -> None:
        current = (*source, key)
        if key in _SCHEMA_MAPS:
            if not isinstance(item, Mapping):
                _fail(current, f"{key} must be a schema map")
            output_key = "definitions" if key == "$defs" else key
            if output_key in result:
                _fail(current, "$defs and definitions cannot both be supplied")
            result[output_key] = {
                name: self.convert(child, (*current, name), (*target, output_key, name)) for name, child in item.items()
            }
        elif key in _SCHEMA_LISTS or key == "prefixItems":
            if not isinstance(item, list):
                _fail(current, f"{key} must be an array of schemas")
            output_key = "items" if key == "prefixItems" else key
            if item or key != "prefixItems":
                result[output_key] = [
                    self.convert(child, (*current, str(index)), (*target, output_key, str(index)))
                    for index, child in enumerate(item)
                ]
        elif key == "items":
            if "prefixItems" in schema:
                if isinstance(item, list):
                    _fail(current, "modern items must be a schema when prefixItems is present")
                output_key = "additionalItems" if schema["prefixItems"] else "items"
                result[output_key] = self.convert(item, current, (*target, output_key))
            elif isinstance(item, list):
                result[key] = [
                    self.convert(child, (*current, str(index)), (*target, key, str(index)))
                    for index, child in enumerate(item)
                ]
            else:
                result[key] = self.convert(item, current, (*target, key))
        elif key in _SCHEMA_VALUES:
            result[key] = self.convert(item, current, (*target, key))
        else:
            result[key] = deepcopy(item)

    def rewrite_references(self) -> None:
        for reference in self.references:
            ref = reference["$ref"]
            if ref.startswith("#/") or ref == "#":
                tokens = (
                    tuple(token.replace("~1", "/").replace("~0", "~") for token in unquote(ref[2:]).split("/"))
                    if ref != "#"
                    else ()
                )
                if tokens in self.locations:
                    reference["$ref"] = _pointer(self.locations[tokens])


def to_asyncapi_schema(value: Mapping[str, Any] | bool) -> dict[str, Any] | bool:
    """Export modern schema keywords to native AsyncAPI Draft07 semantics.

    Only schema positions are traversed. Literal examples, defaults, constants,
    enumerations and extensions remain data. Explicit MultiFormatSchema objects
    must bypass this adapter at the integration boundary.

    Args:
        value: A schema mapping or boolean schema.

    Returns:
        An independent Draft07-compatible schema.

    Raises:
        ImproperlyConfiguredException: If a keyword cannot preserve its meaning
            in Draft07, or a schema position has an invalid shape.
    """
    legacy = isinstance(value, Mapping) and value.get("$schema") in {
        "http://json-schema.org/draft-07/schema#",
        "http://json-schema.org/draft-07/schema",
    }
    converter = _Converter(legacy=legacy)
    converted = converter.convert(value, (), ())
    converter.rewrite_references()
    return converted
