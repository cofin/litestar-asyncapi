=================
Schema Generation
=================

``litestar-asyncapi`` includes an extensible, multi-plugin schema generation engine supporting Python's most popular data modeling libraries.

Supported Type Systems
======================

The schema engine automatically detects and generates JSON Schema representations for the following model paradigms:

- **Msgspec**: Struct definitions, tagged unions, and constraints.
- **Pydantic**: Pydantic v2 and v1 BaseModel models, Field annotations, and validators.
- **Attrs**: ``@define`` and ``@attrs`` decorated classes.
- **Dataclasses**: Standard library ``@dataclass`` decorated classes.
- **TypedDict**: Standard library ``typing.TypedDict`` definitions.
- **Primitive Types**: Standard Python types (``int``, ``float``, ``str``, ``bool``, ``datetime``, ``UUID``).

Msgspec Struct Example
======================

Msgspec structs offer high serialization performance and detailed constraint support:

.. code-block:: python

    import msgspec
    from litestar import websocket_listener


    class UserProfile(msgspec.Struct):
        user_id: str
        display_name: str
        email: str
        reputation: int = 0


    @websocket_listener("/ws/profile")
    async def profile_handler(data: UserProfile) -> UserProfile:
        return data

Pydantic Model Example
======================

Pydantic models integrate with field validators and metadata:

.. code-block:: python

    from litestar import websocket_listener
    from pydantic import BaseModel, Field


    class AlertNotification(BaseModel):
        severity: str = Field(..., pattern="^(info|warning|critical)$")
        message: str
        timestamp: float


    @websocket_listener("/ws/alerts")
    async def alert_handler(data: AlertNotification) -> None:
        pass

Tuple and Sequence Handling
===========================

In accordance with AsyncAPI 3.0 and JSON Schema Draft 2020-12:

- **Fixed-length tuples** (e.g. ``tuple[int, str]``) generate ``prefixItems`` arrays with ``minItems`` and ``maxItems`` constraints to preserve positional typing.
- **Variable-length sequences** (e.g. ``list[str]`` or ``tuple[str, ...]``) generate standard ``items`` array definitions.
