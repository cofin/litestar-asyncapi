Decorator customization
=======================

Place AsyncAPI decorators **above** the Litestar route decorator: they decorate
a route handler, not the undecorated Python function. Always select an explicit
application action, ``receive`` or ``send``.

``asyncapi_operation(messages=[MessageDefinition(...), ...])`` describes multiple
named choices for one action. ``operation_id`` selects the operation map key.
``asyncapi_message`` edits one named message; it rejects an ambiguous unnamed
override when multiple messages exist. Use ``Tag`` objects for tags, not strings.

Explicit metadata overrides inference. Explicit ``messages=[]`` and ``examples=[]``
are intentional empty lists; they do not request fallback inference or generation.
Typed ``MessageExample`` preserves payload, headers, name and summary, including
an explicit null payload. Ordinary example values are wrapped as payloads.

The runnable raw socket validates two incoming choices and describes its response:

.. literalinclude:: ../examples/decorator_overrides/app.py
   :language: python
