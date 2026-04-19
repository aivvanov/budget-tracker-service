from typing import Annotated
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Path  # , Query
from sqlmodel import select

# from app.core.dependencies.dep import CommonHeaders
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryDeleteResponse,
    db_to_category_response,
)  # , CategoriesFilterParams, CategoryImage
from app.models.category import Category
from app.core.dependencies.dep import CommonQueryParams
from app.db.session import SessionDep
from app.auth.security import oauth2_scheme
from app.auth.dependencies import get_current_user_id

router = APIRouter(prefix="/v1/categories", tags=["categories"])


@router.get("/")
async def get_categories(
    commons: Annotated[CommonQueryParams, Depends(CommonQueryParams)],
    # filter_query: Annotated[CategoriesFilterParams, Query()],
    token: Annotated[str, Depends(oauth2_scheme)],
    session: SessionDep,
    user_id: Annotated[str, Depends(get_current_user_id)],
) -> list[CategoryResponse]:

    categories = session.exec(
        select(Category)
        .where(
            Category.user_id == user_id,
            Category.created_at >= commons.date_from,
            Category.created_at <= commons.date_to,
        )
        .offset(commons.offset)
        .limit(commons.limit)
    ).all()

    return [db_to_category_response(cat) for cat in categories]


@router.get("/{id}")
async def get_category(
    id: Annotated[str, Path(title="The ID of the category to get")],
    session: SessionDep,
    token: Annotated[str, Depends(oauth2_scheme)],
    user_id: Annotated[str, Depends(get_current_user_id)],
) -> CategoryResponse:

    category = session.exec(
        select(Category).where(Category.id == id, Category.user_id == user_id)
    ).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return db_to_category_response(category)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_category(
    category: CategoryCreate,
    session: SessionDep,
    token: Annotated[str, Depends(oauth2_scheme)],
    user_id: Annotated[str, Depends(get_current_user_id)],
) -> CategoryResponse:

    user_category = session.exec(
        select(Category).where(
            Category.name == category.name, Category.user_id == user_id
        )
    ).first()
    if user_category:
        raise HTTPException(
            status_code=400,
            detail=f'Category with name "{user_category.name}" already exists',
        )

    db_category = Category(
        name=category.name,
        icon_url=category.icon_url,
        is_income=category.is_income,
        user_id=user_id,
    )
    db_category.created_at = datetime.now(timezone.utc)
    db_category.updated_at = None

    session.add(db_category)
    session.commit()
    session.refresh(db_category)

    return db_to_category_response(db_category)


@router.patch("/{id}")
async def update_category(
    id: str,
    category: CategoryUpdate,
    session: SessionDep,
    token: Annotated[str, Depends(oauth2_scheme)],
    user_id: Annotated[str, Depends(get_current_user_id)],
) -> CategoryResponse:

    category_db = session.exec(
        select(Category).where(Category.id == id, Category.user_id == user_id)
    ).first()
    if not category_db:
        raise HTTPException(status_code=404, detail="Category not found")

    category_data = category.model_dump(exclude_unset=True, exclude=None)
    category_db.updated_at = datetime.now(timezone.utc)
    category_db.icon_url = category.icon_url
    category_db.sqlmodel_update(category_data)

    session.add(category_db)
    session.commit()
    session.refresh(category_db)

    return db_to_category_response(category_db)


@router.delete("/{id}")
async def delete_category(
    id: Annotated[int, Path],
    session: SessionDep,
    token: Annotated[str, Depends(oauth2_scheme)],
    user_id: Annotated[str, Depends(get_current_user_id)],
) -> CategoryDeleteResponse:

    category = session.exec(
        select(Category).where(Category.id == id, Category.user_id == user_id)
    ).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    session.delete(category)
    session.commit()
    return CategoryDeleteResponse(category_id=id)


# @router.post(
#     "/file",
#     tags=["files"]
# )
# async def upload_file(
#     file: Annotated[UploadFile, File()]
# ):
#     """Upload a file"""
#     content = await file.read()
#     return Response(content=content, media_type="application/octet-stream")
