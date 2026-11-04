from litestar_asyncapi.spec.bindings import WebSocketChannelBinding


def test_websocket_binding_serialization() -> None:
    binding = WebSocketChannelBinding(binding_version="0.1.0", method="GET")
    data = binding.to_schema()
    assert data["bindingVersion"] == "0.1.0"
    assert data["method"] == "GET"
