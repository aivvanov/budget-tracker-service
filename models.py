from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime, timedelta
from typing import Literal
import uuid

class CommonQueryParams:
    def __init__(self, q: str | None = None, offset: int = 0, limit: int = 10):
        self.q = q
        self.offset = offset
        self.limit = limit

class BaseDependancies:
    def __init__(self, x_system_id: str | None = None):
        self.x_system_id = x_system_id


class User(BaseModel):
    email: str | None = None
    username: str
    full_name: str | None = None
    disabled: bool | None = None

class UserInDB(User):
    hashed_password: str


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


class CategoryImage(BaseModel):
    url: HttpUrl
    name: str


class Category(BaseModel):
    name: str = "unknown"
    description : str | None = None
    tags: set[str] = set()
    image: CategoryImage | None = None


class CategoriesFilterParams(BaseModel):
    order_by: Literal["created_at", "updated_at"] = "created_at"


class CommonHeaders(BaseModel):
    host: str
    save_data: bool
    if_modified_since: str | None = None
    traceparent: str | None = None
    x_tag: list[str] = []


class FormDataIn(BaseModel):
    username: str
    password: str


class FormDataOut(BaseModel):
    username: str


mock_transactions = [
    TransactionOut(
        amount=1200.5,
        category='salary',
        date=datetime.now() - timedelta(days=10),
        description='Месячная зарплата'
    ).model_dump(),
    TransactionOut(
        amount=-320,
        category='food',
        date=datetime.now() - timedelta(days=7),
        description='Покупка продуктов'
    ).model_dump(),
    TransactionOut(
        amount=-501.2,
        category='transport',
        date=datetime.now() - timedelta(days=3),
        description='Такси до аэропорта'
    ).model_dump(),
    TransactionOut(
        amount=250.0,
        category='freelance',
        date=datetime.now() - timedelta(days=20),
        description='Проект по автоматизации'
    ).model_dump(),
]

mock_users = {"alexatom": {
                "email":"alex@gmail.com", 
                "username":"alexatom", 
                "hashed_password": "fakehashedsecret",
                "full_name":"Alex Ivanov", 
                "disabled":False
                },
            "aprilluna": {
                "email":"april@gmail.com", 
                "username":"aprilluna",
                "hashed_password":"fakehashedsecret2",
                "full_name":"April Luna", 
                "disabled":True
            }
}