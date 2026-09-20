import pytest

from litestar_asyncapi import AsyncAPIConfig
from litestar_asyncapi.spec import Server

pytestmark = pytest.mark.anyio


def test_config_defaults() -> None:
    config = AsyncAPIConfig()
    assert config.default_content_type is None
    assert config.use_handler_docstrings is False
    assert config.create_examples is False
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


def test_nested_docs_options_and_document_version() -> None:
    from litestar import Litestar

    from litestar_asyncapi import DocsConfig
    from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator

    config = AsyncAPIConfig(spec_version="3.0.0", docs=DocsConfig(path="/events", enable_routes=False))
    assert config.docs.path == "/events"
    assert config.docs.renderer == "asyncapi"
    assert config.docs.interactive is False
    assert not hasattr(config.docs, "__dict__")
    assert AsyncAPIGenerator(Litestar([]), config).build_schema()["asyncapi"] == "3.0.0"
