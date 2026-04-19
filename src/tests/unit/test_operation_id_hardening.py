import pytest
from litestar import Litestar, websocket
from litestar.exceptions import ImproperlyConfiguredException
from litestar.status_codes import HTTP_200_OK

from litestar_asyncapi import AsyncAPIConfig
from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator


def test_operation_id_case_insensitive_collision() -> None:
    @websocket("/op1", operation_id="myOp")
    async def handler1(socket: any) -> None:
        pass

    @websocket("/op2", operation_id="MYOP")
    async def handler2(socket: any) -> None:
        pass

    app = Litestar(route_handlers=[handler1, handler2])
    print(f"HANDLER 1 OPT: {handler1.opt}")
    config = AsyncAPIConfig()
    generator = AsyncAPIGenerator(app, config)
    
    schema = generator.build_asyncapi()
    
    op_ids = [op.operation_id for op in schema.operations.values()]
    print(f"OP IDS: {op_ids}")
    
    # Should have 4 unique IDs, not a collision on 'myop_receive'
    assert len(op_ids) == 4
    # All should be unique case-insensitively
    assert len({id.casefold() for id in op_ids}) == 4


def test_strict_uniqueness_raises_exception() -> None:
    @websocket("/op1", operation_id="myOp")
    async def handler1(socket: any) -> None:
        pass

    @websocket("/op2", operation_id="myOp")
    async def handler2(socket: any) -> None:
        pass

    app = Litestar(route_handlers=[handler1, handler2])
    # Assuming we will add strict_uniqueness to AsyncAPIConfig
    config = AsyncAPIConfig(strict_uniqueness=True)
    generator = AsyncAPIGenerator(app, config)
    
    with pytest.raises(ImproperlyConfiguredException, match="Duplicate operationId found"):
        generator.build_asyncapi()
