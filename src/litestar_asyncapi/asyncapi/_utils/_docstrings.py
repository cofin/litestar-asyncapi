import inspect
from typing import Any

__all__ = ("get_handler_docstring",)


def get_handler_docstring(handler: Any) -> str | None:
    """Return a normalized docstring for a handler or callable.

    Args:
        handler: A Litestar route handler or callable object.

    Returns:
        The normalized docstring, or ``None`` if no docstring is available.
    """

    for candidate in _iter_docstring_candidates(handler):
        docstring = inspect.getdoc(candidate)
        if docstring:
            return docstring.strip() or None
    return None


def _iter_docstring_candidates(handler: Any) -> list[Any]:
    candidates: list[Any] = []
    seen: set[int] = set()

    def _add(value: Any) -> None:
        if id(value) in seen:
            return
        seen.add(id(value))
        candidates.append(value)

    def _add_with_inner(value: Any) -> None:
        if value is None:
            return
        inner = getattr(value, "_fn", None)
        if inner is not None:
            _add(inner)
        _add(value)

    for attr in ("fn", "_fn", "handler_fn", "handler", "_handler", "callable"):
        _add_with_inner(getattr(handler, attr, None))
    _add(handler)

    return candidates
