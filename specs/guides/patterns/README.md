# Pattern Library

This directory contains reusable patterns extracted from completed features.

## How Patterns Are Captured

1. During implementation, new patterns are documented in `tmp/new-patterns.md`
2. During review, patterns are extracted to this directory
3. Future PRD phases consult this library first

## Pattern Categories

### Plugin Patterns

- InitPluginProtocol implementation
- Configuration dataclass patterns
- App lifecycle hooks

### Schema Generation Patterns

- AsyncAPI spec generation
- Channel definitions
- Message schema mapping

### Type Handling Patterns

- Type converters for AsyncAPI types
- Schema mappings from Python types
- Validation patterns

### Testing Patterns

- Fixture patterns (conftest.py)
- Mock strategies for Litestar apps
- Integration test setups

### Error Handling Patterns

- Exception hierarchies
- Recovery strategies
- Logging patterns

## Using Patterns

When starting a new feature:

1. Search this directory for similar patterns
2. Read pattern documentation before implementation
3. Follow established conventions
4. Add new patterns during review phase

## Existing Project Patterns (Extracted from Codebase)

### Plugin Class Pattern

```python
from typing import TYPE_CHECKING

from litestar.plugins import InitPluginProtocol

if TYPE_CHECKING:
    from litestar.config.app import AppConfig

class MyPlugin(InitPluginProtocol):
    """Plugin description using Google-style docstrings."""

    __slots__ = ("_config",)

    def __init__(self, config: MyConfig | None = None) -> None:
        self._config = config or MyConfig()

    @property
    def config(self) -> MyConfig:
        return self._config

    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        # Plugin initialization logic
        return app_config
```

### Configuration Dataclass Pattern

```python
from dataclasses import dataclass, field

@dataclass
class MyConfig:
    """Configuration for the plugin.

    Attributes documented as inline comments under each field.
    """

    title: str = "Default Title"
    """The title field description."""
    version: str = "1.0.0"
    """The version field description."""
    optional_field: str | None = None
    """Optional fields use PEP 604 T | None syntax."""
    dict_field: dict[str, str] = field(default_factory=dict)
    """Dict fields use field(default_factory=...)."""
```

### Test Fixture Pattern

```python
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from litestar import Litestar

pytestmark = pytest.mark.anyio

@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"

@pytest.fixture
def my_config() -> MyConfig:
    from mypackage import MyConfig
    return MyConfig(title="Test")

@pytest.fixture
def app(my_plugin: MyPlugin) -> Litestar:
    from litestar import Litestar
    return Litestar(plugins=[my_plugin])
```

### Function-Based Test Pattern

```python
def test_feature_description() -> None:
    """Test docstring describing what is being tested."""
    from mypackage import SomeClass

    result = SomeClass()
    assert result.field == "expected"
```
