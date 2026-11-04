from typing import Any

import pytest

from litestar_asyncapi.asyncapi import generator


@pytest.fixture(autouse=True)
def discovered_channel_keys_are_unique(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fail any integration test whose application discovery yields two channels with one key."""
    discover = generator._discover_channels

    def checked(*args: Any, **kwargs: Any) -> Any:
        channels = discover(*args, **kwargs)
        keys = [channel.key for channel in channels]
        assert len(keys) == len(set(keys)), f"duplicate discovered channel keys: {sorted(keys)}"
        return channels

    monkeypatch.setattr(generator, "_discover_channels", checked)
