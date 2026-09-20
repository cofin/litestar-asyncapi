Schema generation
=================

The adapter uses Litestar's native ``SchemaCreator``, ``FieldDefinition`` and a
fresh registry with ``app.plugins.openapi``. It supports the model systems enabled
in the installed Litestar application, including dataclasses, msgspec, Pydantic,
attrs and TypedDict. Install their native optional integrations when needed.
There is no separate AsyncAPI type-plugin registry.

A native schema plugin also works with ``openapi_config=None``:

.. literalinclude:: ../examples/native_schema.py
   :language: python

The example declares a custom wire string and encoder. A schema plugin describes
a type; it does not install runtime decoding or validation.

Tuple and schema dialect
------------------------

AsyncAPI 3.0/3.1's inline schema dialect is Draft07-compatible. Fixed
``tuple[int, str]`` exports ``items: [{type: integer}, {type: string}]`` with
``minItems: 2`` and ``maxItems: 2``. ``tuple[()]`` has ``maxItems: 0``; bare tuples
and variadic tuples remain unbounded. Native ``prefixItems`` is an internal
representation, not the exported wire keyword. The dialect converter does not
infer cardinality merely from arbitrary ``prefixItems`` input.

Unsupported modern semantics such as dynamic references fail with a schema path.
Explicit ``MultiFormatSchema`` is preserved as an explicit format boundary.
Supported Draft07 wrappers can be rendered by React without changing downloads.
The pinned official schema/parser gate rejects some otherwise valid direct boolean
payloads; use ``MultiFormatSchema("application/schema+json;version=draft-07", False)``
for a conforming boolean payload. Scalar still omits that payload in its display.

Native tuple cardinality, msgspec array-like wire order, recursive references,
model aliases, DTO transfer shapes and explicit null values have focused adapter
corrections. Local forward annotations use the application's
``signature_namespace``; unresolved annotations raise a provenance-rich error.
Bare native ``Schema(default=None)`` or ``Schema(const=None)`` cannot express
whether null was explicitly supplied; field defaults and ``schema_extra`` can.
AsyncAPI's own ``Schema(default=None)`` does preserve null.

Examples
--------

Precedence is explicit message examples, then declared model/schema examples,
then optional native generation with ``create_examples=True``. Empty lists and
nulls remain intentional. Generated values pass through application encoders;
unsupported or unchecked constrained values are omitted with a warning.
Automatic DTO examples are omitted when a reliable native wire value is unavailable.
Use explicit examples for reproducible docs and positional tuple console seeds.
There is no ``random_seed`` or custom factory selector configuration.
