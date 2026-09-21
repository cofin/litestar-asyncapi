from litestar import Litestar, websocket_listener

from litestar_asyncapi import AsyncAPIConfig, AsyncAPIPlugin, DocsConfig, asyncapi_message
from litestar_asyncapi.spec import Server

__all__ = ("app", "http_app")


class Amount:
    __slots__ = ("value",)

    def __init__(self, value: str) -> None:
        self.value = value


@asyncapi_message(action="receive", examples=[(Amount("2.50"), 1)])
@websocket_listener("/events")
async def events(data: tuple[str, int]) -> tuple[str, int]:
    return data


def create_app(*, docs: bool) -> Litestar:
    return Litestar(
        route_handlers=[events],
        type_encoders={Amount: lambda value: f"amount:{value.value}"},
        plugins=[
            AsyncAPIPlugin(
                AsyncAPIConfig(
                    title="Export fixture",
                    version="1.0.0",
                    docs=DocsConfig(enabled=docs),
                    servers={"local": Server(host="localhost:8000", protocol="ws")},
                )
            )
        ],
    )


app = create_app(docs=False)
http_app = create_app(docs=True)
