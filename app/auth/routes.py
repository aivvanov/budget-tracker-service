from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user import UserBase
from app.db.session import SessionDep
from .schemas import Token
from .security import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from .service import authenticate_user
from .dependencies import get_curr_active_user


router = APIRouter(
    prefix="/v1",
    tags=["auth"]
)

@router.get("/users/me",  response_model=UserBase)
async def read_users_me(
    current_user: Annotated[UserBase, Depends(get_curr_active_user)]
    ):
    """Get current user's info"""
    return current_user


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep
    ) -> Token:
    """Get an access token"""
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id, "username": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

