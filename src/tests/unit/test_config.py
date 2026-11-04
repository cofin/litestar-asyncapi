import pytest

from litestar_asyncapi import AsyncAPIConfig
from litestar_asyncapi.spec import Server


def test_config_defaults() -> None:
    config = AsyncAPIConfig()
    assert config.title == "AsyncAPI"
    assert config.version == "1.0.0"
    assert config.description is None
    assert config.servers == {}
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

    config = AsyncAPIConfig(spec_version="3.0.0", docs=DocsConfig(path="/events", enabled=False))
    assert config.docs.path == "/events"
    assert config.docs.renderer == "asyncapi"
    assert config.docs.interactive is False
    assert not hasattr(config.docs, "__dict__")
    assert AsyncAPIGenerator(Litestar([]), config).build_schema()["asyncapi"] == "3.0.0"


@pytest.mark.parametrize("spec_version", ["3.0", "2.6.0", "3.2.0"])
def test_unsupported_spec_version_is_rejected(spec_version: str) -> None:
    with pytest.raises(ValueError, match=rf"Unsupported spec_version '{spec_version}'. Expected '3.0.0' or '3.1.0'."):
        AsyncAPIConfig(spec_version=spec_version)  # type: ignore[arg-type]


@pytest.mark.parametrize("path", ["/", "", "//"])
def test_docs_path_at_the_application_root_is_rejected(path: str) -> None:
    from litestar_asyncapi import DocsConfig

    with pytest.raises(ValueError, match="must not be the application root"):
        DocsConfig(path=path)


def test_docs_path_is_accepted_below_the_root() -> None:
    from litestar_asyncapi import DocsConfig

    assert DocsConfig(path="docs/").path == "docs/"
