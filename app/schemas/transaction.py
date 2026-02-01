from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class TransactionCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    amount: float
    currency: str = Field(default="USD")
    category: str = Field(default="another", index=True)
    description: str | None = Field(default=None)

class TransactionUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    amount: float | None = Field(default=None)
    currency: str | None = Field(default=None)
    category: str | None = Field(default=None)
    description: str | None = Field(default=None)

class TransactionResponse(BaseModel):
    id: int
    amount: float
    currency: str
    category: str
    description: str | None
    created_at: datetime
    updated_at: datetime | None

class TransactionDeleteResponse(BaseModel):
    trx_id: int
    status: str = Field(default="success")
    message: str = Field(default="Transaction deleted successfully")
