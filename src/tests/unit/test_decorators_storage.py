import pytest
from litestar.exceptions import ImproperlyConfiguredException

from litestar_asyncapi.decorators import asyncapi_operation

pytestmark = pytest.mark.anyio


def test_decorators_require_route_handler_instance() -> None:
    def plain() -> None:
        return None

    decorator = asyncapi_operation(action="send", summary="x")
    with pytest.raises(ImproperlyConfiguredException):
        decorator(plain)
