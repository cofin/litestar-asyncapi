from litestar_asyncapi.spec import CorrelationId


def test_correlation_id_to_schema() -> None:
    cid = CorrelationId(
        location="$message.header#/correlationId",
        description="Correlation ID",
    )
    schema = cid.to_schema()
    assert schema["location"] == "$message.header#/correlationId"
    assert schema["description"] == "Correlation ID"


def test_correlation_id_with_extensions() -> None:
    cid = CorrelationId(location="$message.header#/cid")
    cid.extensions["x-provider"] = "aws"
    schema = cid.to_schema()
    assert schema["x-provider"] == "aws"
