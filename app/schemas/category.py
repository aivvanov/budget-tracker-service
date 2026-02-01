from datetime import datetime
from typing import Literal
from pydantic import BaseModel, HttpUrl, Field, ConfigDict
from app.models.category import Category


class CategoryImage(BaseModel):
    url: HttpUrl = Field(default="https://cdn-icons-png.flaticon.com/512/6475/6475885.png")
    name: str

class CategoryCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    name: str | None
    icon: CategoryImage | None
    is_income: bool | None

class CategoryUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    name: str = Field(default=None)
    icon: CategoryImage = Field(default=None)
    is_income: bool = Field(default=None)

class CategoryResponse(BaseModel):
    id: int
    name: str
    icon: CategoryImage
    is_income: bool
    created_at: datetime
    updated_at: datetime | None

class CategoryDeleteResponse(BaseModel):
    category_id: int
    status: str = Field(default="success")
    message: str = Field(default="Category deleted successfully")

class CategoriesFilterParams(BaseModel):
    order_by: Literal["created_at", "updated_at"] = "created_at"


def db_to_category_response(category: Category) -> CategoryResponse:
    """Convert SQLModel Category to Pydantic Response."""
    return CategoryResponse(
        id=category.id,
        name=category.name,
        icon=CategoryImage(url=category.icon_url, name=category.icon_name),
        is_income=category.is_income,
        created_at=category.created_at,
        updated_at=category.updated_at
    )
