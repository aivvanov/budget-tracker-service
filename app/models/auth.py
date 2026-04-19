from datetime import datetime, timedelta
from sqlmodel import Field, SQLModel


class RefreshToken(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    token: str = Field(unique=True)
    user_id: int
    expires_at: datetime = Field(default=lambda: datetime.utcnow() + timedelta(days=7))
