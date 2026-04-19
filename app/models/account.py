from datetime import datetime, timezone
from sqlmodel import Field, SQLModel, Relationship


class Account(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(default="unknown", index=True, max_length=50)
    amount: float
    currency: str = Field(default="USD")
    icon_url: str = Field(default=None, max_length=100)
    user_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = Field(default=None)

    transactions: list["Transaction"] = Relationship(back_populates="account_rel")
