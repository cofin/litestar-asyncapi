"""Metadata for the project."""

from importlib.metadata import PackageNotFoundError, metadata, version

__all__ = ("__project__", "__version__")

try:
    __version__ = version("litestar-asyncapi")
    __project__ = metadata("litestar-asyncapi")["Name"]
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.1.0"
    __project__ = "litestar-asyncapi"
finally:
    del PackageNotFoundError, metadata, version
