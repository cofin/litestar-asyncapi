import pytest

from litestar_asyncapi.asyncapi.datastructures import DiscoveredMessage

pytestmark = pytest.mark.anyio


def test_discovered_message_to_spec_includes_examples() -> None:
    message = DiscoveredMessage(examples=[{"value": 1}])
    spec_message = message.to_spec_message()

    assert spec_message.examples == [{"value": 1}]
