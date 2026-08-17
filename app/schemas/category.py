from datetime import datetime
from typing import Literal
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from app.models.category import Category


class CategoryImageKey(str, Enum):
    GROCERIES = "groceries"
    TRANSPORTATION = "transportation"
    HOME = "home"
    HEALTH = "health"
    LEISURE = "leisure"
    CAFE = "cafe"
    EDUCATION = "education"
    GIFTS = "gifts"
    FAMILY = "family"
    WORKOUT = "workout"
    OTHER = "other"
    SUBSCRIPTIONS = "subscriptions"
    PAYCHECK = "paycheck"
    INTEREST = "interest"


class CategoryCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None
    icon_key: CategoryImageKey | None
    is_income: bool | None


class CategoryUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(default=None)
    icon_key: CategoryImageKey | None
    is_income: bool = Field(default=None)


class CategoryResponse(BaseModel):
    id: int
    name: str
    icon_key: CategoryImageKey | None
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
        icon_key=category.icon_key,
        is_income=category.is_income,
        created_at=category.created_at,
        updated_at=category.updated_at,
    )
