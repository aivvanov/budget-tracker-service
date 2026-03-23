from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str | None = None
    username: str
    full_name: str | None = None
    disabled: bool | None = Field(default=None, index=True)
    default_currency: str | None = "USD"
    hashed_password: str
