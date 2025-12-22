import pytest

from litestar_asyncapi import AsyncAPIConfig
from litestar_asyncapi.spec import Server

pytestmark = pytest.mark.anyio


def test_config_defaults() -> None:
    config = AsyncAPIConfig()
    assert config.default_content_type == "application/json"
    assert config.use_handler_docstrings is False
    assert config.create_examples is False
    assert config.random_seed is None
    assert config.include_websocket_routes is True
    assert config.include_channels_plugin is True
    assert config.use_cache is True


def test_config_to_servers_accepts_server_objects_and_dicts() -> None:
    config = AsyncAPIConfig(
        servers={
            "local": Server(host="localhost:8000", protocol="ws"),
            "prod": {"host": "example.com", "protocol": "wss"},
        }
    )
    servers = config.to_servers()
    assert set(servers) == {"local", "prod"}
    assert servers["local"].protocol == "ws"
    assert servers["prod"].protocol == "wss"
