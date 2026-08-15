from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class TransferCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    from_account_id: int = Field(index=True)
    to_account_id: int = Field(index=True)
    amount: float
    description: str | None
    occurred_at: datetime | None


class TransferUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: float | None = Field(default=None)
    from_account_id: int = Field(index=True)
    to_account_id: int = Field(index=True)
    description: str | None = Field(default=None)
    occurred_at: datetime | None = Field(default=None)


class TransferResponse(BaseModel):
    id: int
    from_account_id: int
    to_account_id: int
    amount: float
    amount_to: float
    description: str | None
    occurred_at: datetime
    created_at: datetime
    updated_at: datetime | None


class TransferDeleteResponse(BaseModel):
    id: int
    status: str = Field(default="success")
    message: str = Field(default="Transfer deleted successfully")
