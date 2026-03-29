from fastapi import APIRouter, status, HTTPException, Depends
from typing import Annotated
from sqlmodel import select
from app.schemas.user import UserInDB, UserCreate, UserBase, DefaultCurrencyUpdate
from app.db.session import SessionDep
from app.auth.service import hash_password
from app.models.user import User
from app.auth.service import get_user
from app.core.dependencies.dep import CommonQueryParams
from app.auth.security import oauth2_scheme
from app.auth.dependencies import get_current_user_id
from app.services.exchange_rate import get_currency_from_db


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
        default_currency = user.default_currency,
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

@router.patch(
    '/external/users/default_currency',
    summary="Change current user's default currency"
)
async def change_curr_user_default_currency(
    commons: Annotated[CommonQueryParams, Depends(CommonQueryParams)],
    token: Annotated[str, Depends(oauth2_scheme)],
    user_id: Annotated[str, Depends(get_current_user_id)],
    session: SessionDep,
    default_currency: DefaultCurrencyUpdate
) -> UserBase:
    currency_db = get_currency_from_db(default_currency.default_currency.upper(), session)
    if not currency_db:
        raise HTTPException(status_code=404, detail=f"Currency {default_currency.default_currency} is not supported.")

    user_db = session.exec(
        select(User)
        .where(
            User.id == user_id
        )
    ).first()
    if not user_db:
         raise HTTPException(status_code=404, detail="User not found")

    user_data = default_currency.model_dump(exclude_unset=True, exclude=None)
    user_data["default_currency"] =  default_currency.default_currency.upper()
    user_db.sqlmodel_update(user_data)

    session.add(user_db)
    session.commit()
    session.refresh(user_db)

    return user_db
