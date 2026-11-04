"""Generate the CLI reference page from the registered Click commands.

The plugin adds its commands to the Litestar CLI through ``register_commands``. The tool registers
them on a fresh ``click.Group`` with a default ``AsyncAPIPlugin`` and writes one section per command
to ``docs/reference/cli.md``, so the page always matches the installed options.
"""

import sys
from pathlib import Path

import click

from litestar_asyncapi import AsyncAPIPlugin
from litestar_asyncapi.cli import register_commands

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "docs" / "reference" / "cli.md"
ROOT_COMMAND = "litestar"
EXAMPLES = {
    "export": [
        "litestar --app app:app asyncapi export",
        "litestar --app app:app asyncapi export --format yaml --output asyncapi.yaml --overwrite",
    ]
}
"""Example invocations shown under each command, keyed by command name."""


def has_default(value: object) -> bool:
    """Return whether an option default should be shown, which excludes Click's unset sentinel."""
    return value is not None and type(value).__name__ != "Sentinel"


def describe_type(option: click.Option) -> str:
    """Return a readable value description for an option."""
    if option.is_flag:
        return "flag"
    if isinstance(option.type, click.Choice):
        return ", ".join(f"`{choice}`" for choice in option.type.choices)
    if isinstance(option.type, click.Path):
        return "file path"
    return option.type.name


def option_rows(command: click.Command) -> list[str]:
    """Return the Markdown table rows for a command's options."""
    rows = []
    for parameter in command.params:
        if not isinstance(parameter, click.Option) or "--help" in parameter.opts:
            continue
        default = f"`{parameter.default}`" if has_default(parameter.default) and not parameter.is_flag else ""
        names = ", ".join(f"`{name}`" for name in parameter.opts)
        rows.append(f"| {names} | {describe_type(parameter)} | {default} | {parameter.help or ''} |")
    return rows


def command_section(path: str, command: click.Command) -> list[str]:
    """Return the Markdown section for one command."""
    lines = [f"## {path}", "", command.help or "", "", "```text", f"{path} [OPTIONS]", "```", ""]
    rows = option_rows(command)
    if rows:
        lines += ["| Option | Value | Default | Description |", "| --- | --- | --- | --- |", *rows, ""]
    examples = EXAMPLES.get(command.name or "", [])
    if examples:
        lines += ["```bash", *examples, "```", ""]
    return lines


def render() -> str:
    """Return the CLI reference page."""
    root = click.Group(ROOT_COMMAND)
    register_commands(root, AsyncAPIPlugin())
    lines = [
        "# CLI",
        "",
        "The plugin adds these commands to the Litestar CLI. They run against the application that",
        "`litestar` discovers or that `--app` names.",
        "",
    ]
    for group_name, group in sorted(root.commands.items()):
        if not isinstance(group, click.Group):
            continue
        lines += [group.help or "", ""]
        for name, command in sorted(group.commands.items()):
            lines += command_section(f"{ROOT_COMMAND} {group_name} {name}", command)
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    """Write the CLI reference page and return a process exit code."""
    OUTPUT.write_text(render(), encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
