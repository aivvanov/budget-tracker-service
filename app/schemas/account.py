from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class AccountCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    name: str = Field(default="unknown")
    amount: float
    currency: str = Field(default="USD")
    icon_url: str = Field(default=None, max_length=100)

class AccountUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    name: str = Field(default="unknown")
    amount: float | None = Field(default=None)
    currency: str | None = Field(default=None)
    icon_url: str = Field(default=None, max_length=100)

class AccountResponse(BaseModel):
    id: int
    name: str
    amount: float
    currency: str
    icon_url: str
    created_at: datetime
    updated_at: datetime | None

class AccountDeleteResponse(BaseModel):
    id: int
    status: str = Field(default="success")
    message: str = Field(default="Account deleted successfully")
