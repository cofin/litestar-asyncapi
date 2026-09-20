from litestar_asyncapi.asyncapi.generator import _channel_key


def test_channel_key() -> None:
    assert _channel_key("/users/{id}") == "/users/{id}"
