from datetime import datetime, timezone
from sqlmodel import Field, SQLModel


class TransactionBase(SQLModel):
    amount: float
    category: str = Field(default="another", index=True)
    description: str | None = Field(default=None)


class Transaction(TransactionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UpdateTransaction(SQLModel):
    amount: float | None
    category: str | None = Field(default="another", index=True)
    description: str | None = Field(default=None)