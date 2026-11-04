# /// script
# requires-python = ">=3.11"
# dependencies = ["litestar[standard]", "litestar-asyncapi"]
# [tool.uv.sources]
# litestar-asyncapi = { path = "../.." }
# ///
"""A typed broker request/reply contract; declaring it creates no broker client."""

from dataclasses import dataclass

from litestar import Litestar

from litestar_asyncapi import (
    AsyncAPIConfig,
    AsyncAPIPlugin,
    ChannelDefinition,
    MessageDefinition,
    OperationDefinition,
    ReplyDefinition,
)

__all__ = ("app",)


@dataclass
class QuoteRequest:
    sku: str
    quantity: int


@dataclass
class Quote:
    sku: str
    total: float


config = AsyncAPIConfig(
    title="Pricing broker",
    channels=[
        ChannelDefinition(
            key="quote-requests",
            address="pricing.requests",
            operations=[
                OperationDefinition(
                    action="receive",
                    operation_id="handleQuoteRequest",
                    messages=[MessageDefinition(name="QuoteRequest", payload=QuoteRequest)],
                    reply=ReplyDefinition("quotes", messages=["Quote"]),
                )
            ],
        ),
        ChannelDefinition(
            key="quotes",
            address="pricing.quotes",
            operations=[
                OperationDefinition(
                    action="send", operation_id="sendQuote", messages=[MessageDefinition(name="Quote", payload=Quote)]
                )
            ],
        ),
    ],
)
app = Litestar(plugins=[AsyncAPIPlugin(config)])
