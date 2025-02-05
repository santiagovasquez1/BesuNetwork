from typing import Any, List
from pydantic import BaseModel


class RpcPayload(BaseModel):
    id: int
    jsonrpc: str
    method: str
    params: List[Any]