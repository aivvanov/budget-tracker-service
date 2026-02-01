from typing import Annotated
from datetime import datetime, timezone
from fastapi import APIRouter, Query, Depends, HTTPException, status, Path
from sqlmodel import select
from app.core.dependencies.dep import CommonHeaders
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryDeleteResponse, CategoriesFilterParams, CategoryImage, db_to_category_response
from app.models.category import Category
from app.core.dependencies.dep import CommonQueryParams
from app.db.session import SessionDep
from app.auth.security import oauth2_scheme

router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)

@router.get('/')
async def get_categories(
    commons: Annotated[CommonQueryParams, Depends(CommonQueryParams)],
    #filter_query: Annotated[CategoriesFilterParams, Query()],
    token: Annotated[str, Depends(oauth2_scheme)],
    session: SessionDep
) -> list[CategoryResponse]:
    categories = session.exec(
        select(Category)
        .offset(commons.offset)
        .limit(commons.limit)
    ).all()

    return [db_to_category_response(cat) for cat in categories]

@router.get('/{id}')
async def get_category(
    id: Annotated[str, Path(title='The ID of the category to get')],
    session: SessionDep,
    token: Annotated[str, Depends(oauth2_scheme)]
) -> CategoryResponse:
    category = session.get(Category, id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return db_to_category_response(category)

@router.post(
    '/', 
    status_code=status.HTTP_201_CREATED
)
async def add_category(
    category: CategoryCreate,
    session: SessionDep,
    token: Annotated[str, Depends(oauth2_scheme)]
) -> CategoryResponse:
    db_category = Category(
        name=category.name,
        icon_url=str(category.icon.url),
        icon_name=category.icon.name,
        is_income=category.is_income
    )
    db_category.created_at = datetime.now(timezone.utc)
    db_category.updated_at = None

    session.add(db_category)
    session.commit()
    session.refresh(db_category)

    return db_to_category_response(db_category)

@router.delete("/{trx_id}")
async def delete_category(
    id: int,
    session: SessionDep,
    token: Annotated[str, Depends(oauth2_scheme)]
) -> CategoryDeleteResponse:
    category = session.get(Category, id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    session.delete(category)
    session.commit()
    return CategoryDeleteResponse(category_id=id)

#TO DO: fix an ability to update icon info
@router.patch('/{trx_id}')
async def update_category(
    id: str, 
    category: CategoryUpdate,
    session: SessionDep,
    token: Annotated[str, Depends(oauth2_scheme)]
) -> CategoryResponse:
    category_db = session.get(Category, id)
    if not category_db:
        raise HTTPException(status_code=404, detail="Category not found")

    category_data = category.model_dump(exclude_unset=True, exclude=None)
    category_db.updated_at = datetime.now(timezone.utc)
    category_db.sqlmodel_update(category_data)

    session.add(category_db)
    session.commit()
    session.refresh(category_db)

    return db_to_category_response(category_db)

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
