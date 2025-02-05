from pydantic import BaseModel


class PodInformation(BaseModel):
    name: str
    dns: str
    ip: str
