from litestar_asyncapi.spec import Tag, ExternalDocumentation


def test_tag_to_schema() -> None:
    tag = Tag(
        name="user",
        description="User operations",
        external_docs=ExternalDocumentation(url="https://example.com"),
    )
    schema = tag.to_schema()
    assert schema["name"] == "user"
    assert schema["description"] == "User operations"
    assert schema["externalDocs"]["url"] == "https://example.com"


def test_tag_with_extensions() -> None:
    tag = Tag(name="user")
    tag.extensions["x-internal"] = True
    schema = tag.to_schema()
    assert schema["x-internal"] is True
