"""Exercise the supported boundary around Litestar's private schema adapter."""

import pytest
from litestar.exceptions import ImproperlyConfiguredException

from litestar_asyncapi import _compat
from litestar_asyncapi.asyncapi.schema_generation import AsyncAPISchemaGenerator


def test_incompatible_native_adapter_reports_payload_and_origin(monkeypatch: pytest.MonkeyPatch) -> None:
    def incompatible(*args: object, **kwargs: object) -> None:
        message = "native schema signature mismatch"
        raise TypeError(message)

    monkeypatch.setattr(_compat._SchemaCreator, "for_field_definition", incompatible)
    with pytest.raises(
        ImproperlyConfiguredException, match=r"Cannot generate AsyncAPI payload.*str.*route /events"
    ) as caught:
        AsyncAPISchemaGenerator().generate(str, provenance="route /events receive")
    assert isinstance(caught.value.__cause__, TypeError)
    assert "native schema signature mismatch" in str(caught.value)
