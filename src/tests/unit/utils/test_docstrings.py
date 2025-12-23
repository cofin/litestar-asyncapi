from dataclasses import dataclass

import pytest

from litestar_asyncapi.asyncapi.utils.docstrings import get_handler_docstring

pytestmark = pytest.mark.anyio


def test_get_handler_docstring_normalizes_docstring() -> None:
    def handler() -> None:
        """Summary line.

        Additional details.
        """

    assert get_handler_docstring(handler) == "Summary line.\n\nAdditional details."


def test_get_handler_docstring_reads_handler_fn_attribute() -> None:
    def handler() -> None:
        """Handler documentation."""

    @dataclass
    class Dummy:
        fn: object

    wrapper = Dummy(handler)
    assert get_handler_docstring(wrapper) == "Handler documentation."


def test_get_handler_docstring_returns_none_when_missing() -> None:
    def handler() -> None:
        return None

    assert get_handler_docstring(handler) is None
