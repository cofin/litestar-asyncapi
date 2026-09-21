from pathlib import Path
from typing import TYPE_CHECKING

import click
from litestar import Litestar
from yaml import safe_dump  # type: ignore[import-untyped]

if TYPE_CHECKING:
    from litestar_asyncapi.plugins import AsyncAPIPlugin

__all__ = ("register_commands",)


def register_commands(cli: click.Group, plugin: "AsyncAPIPlugin") -> None:
    """Register export commands using the native CLI group's application injection."""

    @cli.group(name="asyncapi")
    def asyncapi_group() -> None:
        """Export AsyncAPI documents without starting a server."""

    @asyncapi_group.command(name="export")
    @click.option("--format", "format_", type=click.Choice(["json", "yaml"]), default="json", show_default=True)
    @click.option("--output", type=click.Path(path_type=Path, dir_okay=False))
    @click.option("--overwrite", is_flag=True, help="Replace an existing output file.")
    def export(app: Litestar, format_: str, output: Path | None, overwrite: bool) -> None:
        """Write the canonical application document to a file or stdout."""
        try:
            content = (
                safe_dump(plugin.get_asyncapi_schema(app), sort_keys=True, allow_unicode=True)
                if format_ == "yaml"
                else plugin.get_asyncapi_json(app).decode("utf-8") + "\n"
            )
            if output is None:
                click.echo(content, nl=False)
            else:
                with output.open("w" if overwrite else "x", encoding="utf-8") as file:
                    file.write(content)
        except FileExistsError as exc:
            message = f"Output already exists: {output}. Use --overwrite to replace it."
            raise click.ClickException(message) from exc
        except Exception as exc:
            message = f"AsyncAPI export failed: {exc}"
            raise click.ClickException(message) from exc
