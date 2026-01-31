from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from .security import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from .service import authenticate_user
from .dependencies import get_curr_active_user
from .schemas import mock_users, User, Token

router = APIRouter()

@router.get("/users/me",  response_model=User, tags=["auth"])
async def read_users_me(
    current_user: Annotated[User, Depends(get_curr_active_user)]
    ):
    """Get current user's info"""
    return current_user


@router.post("/token", tags=["auth"])
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
    ) -> Token:
    """Get an access token"""
    user = authenticate_user(mock_users, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
