# Exporting documents

The plugin adds an `asyncapi export` command to the Litestar CLI. This application describes a broker with explicit contracts and has no routes:

```python
--8<-- "docs/examples/contracts.py"
```

Export its document from a checkout of this repository:

```bash
uv run litestar --app docs.examples.contracts:app asyncapi export --output asyncapi.json
uv run litestar --app docs.examples.contracts:app asyncapi export --format yaml --output asyncapi.yaml
```

## The exported document

The export is the same canonical document that the documentation routes serve. Its operations section:

```json
--8<-- "docs/_generated/fragments/contracts/operations.json"
```

## How it works

The command loads the application through Litestar's own `--app` option or autodiscovery, builds the document and writes it without starting a server. It does not need the documentation routes, so it works with `DocsConfig(enabled=False)`.

Without `--output`, the document goes to stdout. `--format yaml` writes YAML instead of JSON. An existing file is replaced only with `--overwrite`; otherwise the command fails with a message on stderr and a non-zero exit code, as it does when the document cannot be built.

Exports use the application's type encoders and the servers declared in the configuration, so a committed export matches what the running application serves. To check it in continuous integration, export to a file and compare it with the committed copy, or validate it with the [AsyncAPI CLI](https://www.asyncapi.com/docs/tools/cli), which also handles conversion and code generation.

Inside Python, `AsyncAPIPlugin.get_asyncapi_schema(app)` returns the same document as a dictionary and `get_asyncapi_json(app)` as JSON bytes.

## Recap

- `litestar asyncapi export` writes the document as JSON or YAML without starting a server.
- Existing files are kept unless `--overwrite` is given.
- Next, browse the [runnable examples](examples.md); the [CLI reference](../reference/cli.md) lists every option.
