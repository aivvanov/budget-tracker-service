from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel, Relationship


class Transfer(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    from_account_id: int = Field(foreign_key="account.id")
    to_account_id: int = Field(foreign_key="account.id")
    amount: float  # from_account currency
    amount_to: float | None  # to_account currency (in case it's different)
    description: str | None
    user_id: str = Field(index=True)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = Field(default=None)

    from_account: Optional["Account"] = Relationship(
        back_populates="outgoing_transfers",
        sa_relationship_kwargs={"foreign_keys": "[Transfer.from_account_id]"},
    )
    to_account: Optional["Account"] = Relationship(
        back_populates="incoming_transfers",
        sa_relationship_kwargs={"foreign_keys": "[Transfer.to_account_id]"},
    )
