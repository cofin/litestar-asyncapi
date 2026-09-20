from copy import deepcopy
from typing import TYPE_CHECKING, Any

from litestar.enums import MediaType
from litestar.exceptions import ImproperlyConfiguredException, NotFoundException
from litestar.handlers import get
from litestar.plugins import InitPluginProtocol
from litestar.response import Response
from litestar.router import Router
from litestar.serialization import encode_json
from litestar.static_files import create_static_files_router
from litestar.status_codes import HTTP_404_NOT_FOUND

from litestar_asyncapi.docs import asset_directory, renderer_name
from litestar_asyncapi.serialization import normalize_document

if TYPE_CHECKING:
    from click import Group
    from litestar import Litestar
    from litestar.config.app import AppConfig
    from litestar.handlers import HTTPRouteHandler

    from litestar_asyncapi.config import AsyncAPIConfig
    from litestar_asyncapi.plugins import AsyncAPIRenderPlugin
    from litestar_asyncapi.spec import AsyncAPI

__all__ = ("AsyncAPIPlugin",)


def _handle_docs_path_not_found(path: str = "/") -> Response[Any]:
    if path.endswith((".json", ".yaml", ".yml")):
        raise NotFoundException

    content = b"""
    <!DOCTYPE html>
    <html>
        <head>
            <title>404 Not found</title>
            <meta charset="utf-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1">
        </head>
        <body>
            <h1>Error 404</h1>
        </body>
    </html>
    """
    return Response(content, media_type=MediaType.HTML, status_code=HTTP_404_NOT_FOUND)


class AsyncAPIPlugin(InitPluginProtocol):
    """AsyncAPI plugin for Litestar.

    This plugin provides AsyncAPI documentation support for event-driven APIs,
    similar to how OpenAPI documents REST APIs.
    """

    __slots__ = ("_app", "_cached_asyncapi", "_cached_json", "_cached_schema", "_config")

    def __init__(self, config: "AsyncAPIConfig | None" = None) -> None:
        """Initialize the AsyncAPI plugin.

        Args:
            config: Optional AsyncAPI configuration. If not provided, defaults will be used.
        """
        from litestar_asyncapi.config import AsyncAPIConfig

        self._config = config or AsyncAPIConfig()
        self._app: Litestar | None = None
        self._cached_json: bytes | None = None
        self._cached_asyncapi: AsyncAPI | None = None
        self._cached_schema: dict[str, Any] | None = None

    @property
    def config(self) -> "AsyncAPIConfig":
        """Return the plugin configuration.

        Returns:
            The AsyncAPI configuration instance.
        """
        return self._config

    def clear_cache(self) -> None:
        """Clear generated values while retaining ownership of the bound application."""
        self._cached_asyncapi = None
        self._cached_schema = None
        self._cached_json = None

    def _get_document(self, app: "Litestar") -> tuple["AsyncAPI", dict[str, Any], bytes]:
        if self._app is None:
            self._app = app
        elif self._app is not app:
            message = (
                "An AsyncAPIPlugin instance belongs to one application; create a separate plugin for each application"
            )
            raise ImproperlyConfiguredException(message)
        if (
            self.config.use_cache
            and self._cached_asyncapi is not None
            and self._cached_schema is not None
            and self._cached_json is not None
        ):
            return self._cached_asyncapi, self._cached_schema, self._cached_json

        from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator

        document = deepcopy(AsyncAPIGenerator(app=app, config=self.config).build_asyncapi())
        schema = normalize_document(document, app.type_encoders)
        encoded = encode_json(schema)
        if self.config.use_cache:
            self._cached_asyncapi, self._cached_schema, self._cached_json = document, schema, encoded
        return document, schema, encoded

    def get_asyncapi(self, app: "Litestar") -> "AsyncAPI":
        """Return a defensive copy of the application document."""
        return deepcopy(self._get_document(app)[0])

    def get_asyncapi_schema(self, app: "Litestar") -> dict[str, Any]:
        """Return a defensive copy of the canonical JSON-compatible document."""
        return deepcopy(self._get_document(app)[1])

    def get_asyncapi_json(self, app: "Litestar") -> bytes:
        """Return immutable canonical JSON bytes for the bound application."""
        return self._get_document(app)[2]

    def create_docs_router(self) -> Router:
        """Create a router for serving AsyncAPI documentation and schema files.

        Returns:
            A Litestar router that serves all configured render plugin paths.
        """
        router = Router(
            self.config.docs.path,
            route_handlers=[],
            include_in_schema=False,
            dto=None,
            return_dto=None,
            guards=list(self.config.docs.guards),
            dependencies=self.config.docs.dependencies,
        )
        plugins = self.config.docs.render_plugins or []
        names = {"assets": "asyncapi:assets"}
        for plugin in plugins:
            name = renderer_name(plugin)
            key = name.removeprefix("asyncapi:")
            if key == "AsyncAPIUIRenderPlugin":
                key = "ui"
            elif key == "AsyncAPIPlaygroundRenderPlugin":
                key = "playground"
            names[key] = name
        router.register(create_static_files_router("/assets", directories=[asset_directory()], name=names["assets"]))

        def create_handler(plugin: "AsyncAPIRenderPlugin") -> "HTTPRouteHandler":
            paths = list(plugin.paths)

            @get(
                paths,
                name=renderer_name(plugin),
                opt={"asyncapi_routes": names},
                media_type=plugin.media_type,
                sync_to_thread=False,
            )
            def _handler(request: Any) -> bytes:
                return plugin.render(request, self.get_asyncapi_schema(request.app))

            return _handler

        for render_plugin in plugins:
            router.register(create_handler(render_plugin))

        root_configured = any(p.has_path("/") for p in plugins)
        not_found_handler_paths = ["/{path:str}"]
        if not root_configured:
            not_found_handler_paths.append("/")

        router.register(
            get(not_found_handler_paths, media_type=MediaType.HTML, sync_to_thread=False)(_handle_docs_path_not_found)
        )

        for render_plugin in plugins:
            render_plugin.receive_router(router)

        return router

    def on_cli_init(self, cli: "Group") -> None:
        """Extend Litestar's CLI with headless AsyncAPI export."""
        from litestar_asyncapi.cli import register_commands

        register_commands(cli, self)

    def on_app_init(self, app_config: "AppConfig") -> "AppConfig":
        """Handle application initialization.

        This method is called during Litestar application initialization.
        Registers docs routes when enabled.

        Args:
            app_config: The Litestar application configuration.

        Returns:
            The updated application configuration.
        """
        if self.config.docs.enabled:
            app_config.route_handlers.append(self.create_docs_router())
        return app_config
