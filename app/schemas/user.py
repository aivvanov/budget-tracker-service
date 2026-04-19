from datetime import datetime
from pydantic import BaseModel


class UserCreate(BaseModel):
    """Schema for creating new user with plain password"""

    email: str | None = None
    username: str
    full_name: str | None = None
    password: str
    default_currency: str | None = "USD"


class UserBase(BaseModel):
    email: str | None = None
    username: str
    full_name: str | None = None
    disabled: bool | None = None
    default_currency: str | None = "USD"
    created_at: datetime
    updated_at: datetime | None


class UserInDB(UserBase):
    hashed_password: str


class DefaultCurrencyUpdate(BaseModel):
    default_currency: str
