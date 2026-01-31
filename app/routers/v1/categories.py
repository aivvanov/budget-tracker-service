from typing import Annotated
from fastapi import APIRouter, UploadFile, Response, File, status, Body, Header
from app.core.dependencies.dep import CommonHeaders
from app.schemas.category import Category

router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)

@router.get('/')
async def get_category(
                        #filter_query: Annotated[CategoriesFilterParams, Query()],
                        headers: Annotated[CommonHeaders, Header()],
                        #commons: Annotated[CommonQueryParams, Depends(CommonQueryParams)],
                        #ads_id: Annotated[str | None, Cookie()] = None
                        ):
    """List all existing categories."""
    return headers


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_category(category: Category,
                        importance: Annotated[int | None, Body(ge=0, le=10)]
                        = None
                    ):
    """Create a new category"""
    result = category.model_dump()
    if importance:
        result.update({"importance": importance})
    return result


@router.post("/file", tags=["files"])
async def upload_file(file: Annotated[UploadFile, File()]):
    """Upload a file"""
    content = await file.read()
    return Response(content=content, media_type="application/octet-stream")
