=======================
Concepts & Architecture
=======================

AsyncAPI 3.0 provides a machine-readable specification for event-driven and message-based APIs. This page describes how ``litestar-asyncapi`` models and generates AsyncAPI entities from Litestar applications.

Document Structure
==================

An AsyncAPI 3.0 document comprises five main sections:

1. **Info**: Application metadata, version, license, and contact details.
2. **Servers**: Connection targets (e.g. WebSocket hosts and protocols) with optional security schemes.
3. **Channels**: Named message paths (e.g. ``/ws/notifications`` or ``chat.{room_id}``) defining addressable communication destinations.
4. **Operations**: Actions that clients or servers perform over channels, partitioned into ``send`` (client sends to server) and ``receive`` (client receives from server).
5. **Components**: Reusable definitions including schemas, messages, server bindings, and security schemes.

Operation Direction Semantics
=============================

AsyncAPI 3.0 defines operation action from the perspective of the application consumer (the client):

- **Send Operation (action="send")**: The client sends a message to the application over the channel. In Litestar, this corresponds to an incoming message parameter received by a WebSocket handler.
- **Receive Operation (action="receive")**: The client receives a message sent by the application over the channel. In Litestar, this corresponds to a message returned or streamed by a WebSocket handler.

Lifecycle & Generation Pipeline
===============================

The ``AsyncAPIPlugin`` integrates with Litestar during application startup:

.. mermaid::

    flowchart TD
        A[Litestar App Init] --> B[AsyncAPIPlugin.on_app_init]
        B --> C[Create Docs Router /asyncapi/]
        B --> D[Register Schema Generator]
        A --> E[First Request or CLI Export]
        E --> F[AsyncAPIGenerator.generate_document]
        F --> G[Route Tree Traversal: Extract Handlers]
        F --> H[ChannelsPlugin Traversal: Extract Pub/Sub]
        G --> I[Schema Registry: Map Types to JSON Schema]
        H --> I
        I --> J[Assemble AsyncAPI 3.0 Document]
        J --> K[Cache Spec & Render UI/JSON/YAML]

Schema Registry & Component Reuse
=================================

The ``SchemaRegistry`` coordinates type inspection across multiple model systems:

- When a data type (e.g. a Msgspec Struct or Pydantic model) is encountered in a handler signature, ``SchemaRegistry`` generates a JSON Schema definition.
- Complex objects are stored in ``components.schemas`` and referenced via JSON Schema pointers (``$ref: "#/components/schemas/<Name>"``).
- This ensures schemas are deduplicated across channels and operations.
