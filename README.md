# litestar-asyncapi

Generate AsyncAPI 3.1 documents from Litestar WebSocket routes and serve packaged documentation. Requires Python 3.10–3.14 and Litestar `>=2.24,<3`. AsyncAPI 3.0 remains available with `spec_version="3.0.0"`.

```python
from dataclasses import dataclass

from litestar import Litestar, websocket_listener
from litestar.dto import DataclassDTO
from litestar_asyncapi import AsyncAPIConfig, AsyncAPIPlugin, DocsConfig
from litestar_asyncapi.spec import Server


@dataclass
class Message:
    text: str


@websocket_listener("/chat", dto=DataclassDTO[Message])
async def chat(data: Message) -> Message:
    return data


app = Litestar(
    [chat],
    plugins=[AsyncAPIPlugin(AsyncAPIConfig(
        title="Chat", version="1.0.0",
        docs=DocsConfig(interactive=True),
        servers={"local": Server(host="localhost:8000", protocol="ws")},
    ))],
)
```

Save as `app.py` and run `uv run litestar --app app:app run`. Open `/asyncapi/` for React documentation and `/asyncapi/asyncapi.json` for JSON. YAML is opt-in with `DocsConfig(yaml=True)`. Python consumers need no Node installation.

Operations describe the application: incoming messages are `receive`, outgoing messages are `send`. Native Litestar schema generation supplies model schemas; fixed tuples export Draft07 positional `items` with exact length bounds.

Interaction defaults to off. The example enables the upstream WebSocket console: **validation is advisory; Send transmits entered text even when invalid**. Supported JSON text object/array contracts can connect to explicit servers. Binary, plain-text, JSON-string and ambiguous contracts remain documentation-only. The application must enforce its own validation and authorization.

AsyncAPI React component 3.2.1 (React 18.3.1) is the default renderer. `DocsConfig(renderer="scalar")` selects Scalar 1.69.2, which omits tuple positions, zero-length bounds and boolean schemas. With `interactive=True`, Scalar links to the shared React console at `/asyncapi/playground`.

Export without starting a server:

```sh
uv run litestar --app app:app asyncapi export
uv run litestar --app app:app asyncapi export --format yaml --output asyncapi.yaml
```

Existing files require `--overwrite`. Export also works with `DocsConfig(enabled=False)`.

See the [migration guide](docs/migration.rst), [runnable examples](docs/examples/README.md), and [usage guides](docs/usage/index.rst). Build documentation with `make docs`.

Development uses `make lint`, `make test`, `make validate-asyncapi`, and the locked Node 22 frontend toolchain. CI tests installed wheels across supported Python versions. Release workflows publish the tested wheel and its accompanying source distribution.
