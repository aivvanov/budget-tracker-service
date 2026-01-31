import uuid
from datetime import datetime
from pydantic import BaseModel, Field

class BaseTransaction(BaseModel):
    amount: int | float
    category: str = 'another'
    date: datetime
    description: str | None = Field(default=None, examples=["The zoo visiting"])


class TransactionOut(BaseTransaction):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class UpdateTransaction(BaseModel):
    amount: int | float | None = None
    category: str | None = None
    date: datetime | None = None
    description: str | None = None
