from pydantic import BaseModel


class AddAccountToBlockchainRequest(BaseModel):
    account_address: str
    private_key: str
    password: str
