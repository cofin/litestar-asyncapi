---
type: Guide
title: Python Style Guide
description: Modern Python development standards, async patterns, typing, and docstring rules.
tags: [styleguide, python, typing, async]
status: stable
generated:
  by: flow-setup
  at: 2026-11-04
---

# Python Style Guide

Modern Python development standards with async-first patterns and strict typing for `litestar-asyncapi`.

## Core Rules

### Type Annotations

- Use PEP 604 union syntax (`str | None`, `int | float`).
- Use PEP 585 built-in types for collections (`list[str]`, `dict[str, Any]`, `tuple[int, ...]`), never `typing` module equivalents.
- Never use `Optional` or `Union` from `typing`.
- Never add `from __future__ import annotations` under `src/litestar_asyncapi/`; the `no_future_annotations` prek hook rejects it because Litestar resolves real annotations at runtime. Import type-only names under `if TYPE_CHECKING:` and quote those annotations.

```python
def get_channel(name: str) -> Channel | None:
    ...

items: list[str] = []
mapping: dict[str, int] = {}
```

### Docstrings and Comments

- **No In-Line Comments:** Never use in-line comments in Python code. If the code requires explanation, add it to the docstring.
- Use Google-style docstrings for public classes, methods, and functions.

```python
def calculate_total(items: list[Item], tax_rate: float) -> Decimal:
    """Calculate the total price including tax.

    Args:
        items: List of items to calculate.
        tax_rate: Tax rate as a decimal (e.g., 0.08 for 8%).

    Returns:
        Total price with tax applied.

    Raises:
        ValueError: If tax_rate is negative.
    """
```

### Async by Default

- All I/O operations must be asynchronous.
- Use `anyio` for asynchronous test suites with `asyncio` event loop backend.

```python
async def fetch_data(url: str) -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()
```

## Slotted Classes & Dataclasses

- Dataclasses and plugin classes should define `__slots__` where applicable to optimize memory layout and performance.
- Verified in CI and pre-commit via `slotscheck`.

```python
@dataclass(slots=True)
class AsyncAPIConfig:
    """Configuration for the AsyncAPI plugin."""
    title: str = "API"
    strict_uniqueness: bool = False
```

## Testing Conventions

- Function-based tests with `pytest`.
- Use `pytestmark = pytest.mark.anyio` for asynchronous tests.
- High test coverage: >90% target for core modules.
