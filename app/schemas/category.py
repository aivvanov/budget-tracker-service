from typing import Literal
from pydantic import BaseModel, HttpUrl

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
