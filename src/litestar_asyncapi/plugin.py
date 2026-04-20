from typing import TYPE_CHECKING, Any

from litestar.enums import MediaType
from litestar.exceptions import NotFoundException
from litestar.handlers import get
from litestar.plugins import InitPluginProtocol
from litestar.response import Response
from litestar.router import Router
from litestar.status_codes import HTTP_404_NOT_FOUND

if TYPE_CHECKING:
    from litestar import Litestar
    from litestar.config.app import AppConfig
    from litestar.handlers import HTTPRouteHandler

    from litestar_asyncapi.config import AsyncAPIConfig
    from litestar_asyncapi.plugins import AsyncAPIRenderPlugin
    from litestar_asyncapi.spec import AsyncAPI


def _handle_docs_path_not_found(path: str = "/") -> Response:
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

    __slots__ = ("_cached_asyncapi", "_cached_schema", "_config")

    def __init__(self, config: "AsyncAPIConfig | None" = None) -> None:
        """Initialize the AsyncAPI plugin.

        Args:
            config: Optional AsyncAPI configuration. If not provided, defaults will be used.
        """
        from litestar_asyncapi.config import AsyncAPIConfig

        self._config = config or AsyncAPIConfig()
        self._cached_asyncapi: AsyncAPI | None = None
        self._cached_schema: dict[str, Any] | None = None

    @property
    def config(self) -> "AsyncAPIConfig":
        """Return the plugin configuration.

        Returns:
            The AsyncAPI configuration instance.
        """
        return self._config

    def invalidate_cache(self) -> None:
        """Invalidate cached AsyncAPI document and schema."""
        self._cached_asyncapi = None
        self._cached_schema = None

    def get_asyncapi(self, app: "Litestar") -> "AsyncAPI":
        """Return a cached or freshly built AsyncAPI document object.

        Args:
            app: The Litestar application instance.

        Returns:
            The built AsyncAPI document.
        """
        if self.config.use_cache and self._cached_asyncapi is not None:
            return self._cached_asyncapi

        from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator

        document = AsyncAPIGenerator(app=app, config=self.config).build_asyncapi()
        if self.config.use_cache:
            self._cached_asyncapi = document
            self._cached_schema = None
        return document

    def get_asyncapi_schema(self, app: "Litestar") -> dict[str, Any]:
        """Return a cached or freshly built AsyncAPI document schema dict.

        Args:
            app: The Litestar application instance.

        Returns:
            A serialized AsyncAPI document dict.
        """
        if self.config.use_cache and self._cached_schema is not None:
            return self._cached_schema

        document = self.get_asyncapi(app)
        schema = document.to_schema()
        if self.config.use_cache:
            self._cached_schema = schema
        return schema

    def create_docs_router(self) -> Router:
        """Create a router for serving AsyncAPI documentation and schema files.

        Returns:
            A Litestar router that serves all configured render plugin paths.
        """
        router = Router(
            self.config.path,
            route_handlers=[],
            include_in_schema=False,
            dto=None,
            return_dto=None,
        )

        plugins: list[AsyncAPIRenderPlugin] = list(self.config.render_plugins)

        def create_handler(plugin: "AsyncAPIRenderPlugin") -> "HTTPRouteHandler":
            paths = list(plugin.paths)

            @get(paths, media_type=plugin.media_type, sync_to_thread=False)
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
            get(not_found_handler_paths, media_type=MediaType.HTML, sync_to_thread=False)(_handle_docs_path_not_found),
        )

        for render_plugin in plugins:
            render_plugin.receive_router(router)

        return router

    def on_app_init(self, app_config: "AppConfig") -> "AppConfig":
        """Handle application initialization.

        This method is called during Litestar application initialization.
        Registers docs routes when enabled.

        Args:
            app_config: The Litestar application configuration.

        Returns:
            The updated application configuration.
        """
        if self.config.enable_routes:
            app_config.route_handlers.append(self.create_docs_router())
        return app_config
