from enum import Enum

__all__ = (
    "OperationAction",
    "SchemaFormat",
    "SchemaType",
    "SecuritySchemeType",
)


class OperationAction(str, Enum):
    """AsyncAPI operation direction (from the application's perspective)."""

    RECEIVE = "receive"
    SEND = "send"


class SchemaType(str, Enum):
    """JSON Schema base types (Draft 07 compatible)."""

    ARRAY = "array"
    BOOLEAN = "boolean"
    INTEGER = "integer"
    NULL = "null"
    NUMBER = "number"
    OBJECT = "object"
    STRING = "string"


class SchemaFormat(str, Enum):
    """Common JSON Schema formats used by AsyncAPI payloads."""

    DATE = "date"
    DATE_TIME = "date-time"
    DURATION = "duration"
    EMAIL = "email"
    HOSTNAME = "hostname"
    IPV4 = "ipv4"
    IPV6 = "ipv6"
    REGEX = "regex"
    URI = "uri"
    UUID = "uuid"


class SecuritySchemeType(str, Enum):
    """AsyncAPI Security Scheme types."""

    API_KEY = "apiKey"
    HTTP = "http"
    OAUTH2 = "oauth2"
    OPEN_ID_CONNECT = "openIdConnect"
    USER_PASSWORD = "userPassword"
    X509 = "X509"
    SYMMETRIC_ENCRYPTION = "symmetricEncryption"
    ASYMMETRIC_ENCRYPTION = "asymmetricEncryption"
    HTTP_API_KEY = "httpApiKey"
