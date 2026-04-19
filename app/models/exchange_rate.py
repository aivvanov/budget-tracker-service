from datetime import datetime
from sqlmodel import SQLModel, Field


class ExchangeRate(SQLModel, table=True):
    __tablename__ = "exchange_rates"

    id: int | None = Field(default=None, primary_key=True)
    from_currency: str = Field(max_length=3)
    to_currency: str = Field(max_length=3)
    rate: float
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
