from pydantic import BaseModel


class UserCreate(BaseModel):
    """Schema for creating new user with plain password"""
    email: str | None = None
    username: str
    full_name: str | None = None
    password: str 

class UserBase(BaseModel):
    email: str | None = None
    username: str
    full_name: str | None = None
    disabled: bool | None = None

class UserInDB(UserBase):
    hashed_password: str
