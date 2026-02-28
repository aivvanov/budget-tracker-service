from datetime import datetime, timezone
from sqlmodel import Field, SQLModel, Relationship
from app.models.category import Category


class Transaction(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    amount: float
    currency: str = Field(default="USD")
    category_id: int | None = Field(default=None, foreign_key="category.id")
    description: str | None = Field(default=None)
    user_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = Field(default=None)
    
    category_rel: Category | None = Relationship(back_populates="transactions")

