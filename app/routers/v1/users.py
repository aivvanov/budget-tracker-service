from fastapi import APIRouter, status, HTTPException, Depends
from typing import Annotated
from sqlmodel import select
from app.schemas.user import UserInDB, UserCreate, UserBase
from app.db.session import SessionDep
from app.auth.service import hash_password
from app.models.user import User
from app.auth.service import get_user
from app.core.dependencies.dep import CommonQueryParams
from app.auth.security import oauth2_scheme


router = APIRouter(
    prefix="/v1",
    tags=["users"]
)


@router.post(
    '/external/users',
    status_code=status.HTTP_201_CREATED,
    response_model=dict
)
async def create_user(
    user: UserCreate,
    session: SessionDep
) -> UserInDB:
    """Add a user to DB"""
    if get_user(session, user.email):
        raise HTTPException(status_code=400, detail="User already exists")
    
    db_user = User(
        email = user.email,
        username=user.username,
        full_name=user.full_name,
        disabled=False,
        hashed_password=hash_password(user.password)
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return {
        "email": db_user.email,
        "status": "created"
    }

@router.get(
    '/internal/users',
    response_model=list[UserBase]
)
async def get_users(
    commons: Annotated[CommonQueryParams, Depends(CommonQueryParams)],
    token: Annotated[str, Depends(oauth2_scheme)],
    session: SessionDep
) -> list[UserBase]:
    return session.exec(
        select(User)
        .offset(commons.offset)
        .limit(commons.limit)
    ).all()
