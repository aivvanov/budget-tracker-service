from datetime import datetime, timedelta, timezone
from typing import Annotated
from sqlmodel import select
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user import UserBase
from app.db.session import SessionDep
from app.models.auth import RefreshToken
from app.models.user import User
from .schemas import Token, RefreshRequest
from .security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    create_refresh_token,
    get_refresh_token_payload,
)
from .service import authenticate_user
from .dependencies import get_curr_active_user

router = APIRouter(prefix="/v1", tags=["auth"])


@router.get("/users/me", response_model=UserBase)
async def read_users_me(
    current_user: Annotated[UserBase, Depends(get_curr_active_user)],
):
    """Get current user's info"""
    return current_user


@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep
) -> Token:
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id, "username": user.username},
        expires_delta=access_token_expires,
    )

    refresh_token_expires = timedelta(minutes=int(REFRESH_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_refresh_token(
        data={"sub": user.email, "user_id": user.id, "username": user.username},
        expires_delta=refresh_token_expires,
    )

    db_token = RefreshToken(
        token=refresh_token,
        user_id=user.id,
        expires_at=datetime.now(timezone.utc) + refresh_token_expires,
    )

    session.add(db_token)
    session.commit()
    session.refresh(db_token)

    return Token(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


@router.post("/token/refresh")
async def refresh_token(data: RefreshRequest, session: SessionDep) -> Token:
    payload = get_refresh_token_payload(data)

    email, user_id = payload.get("sub"), payload.get("user_id")
    if not email or not user_id:
        raise HTTPException(status_code=403, detail="Invalid token payload")

    token_in_db = session.exec(
        select(RefreshToken).where(RefreshToken.token == data.refresh_token)
    ).first()
    if not token_in_db:
        raise HTTPException(status_code=404, detail="Refresh token not found")

    if token_in_db.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        session.delete(token_in_db)
        session.commit()
        raise HTTPException(status_code=401, detail="Refresh token expired")

    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_access_token = create_access_token(
        {"sub": user.email, "user_id": user.id, "username": user.username}
    )
    new_refresh_token = create_refresh_token(
        {"sub": user.email, "user_id": user.id, "username": user.username}
    )

    # Token rotation: delete old and insert new
    session.delete(token_in_db)
    session.add(RefreshToken(token=new_refresh_token, user_id=user.id))
    session.commit()

    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
    )


@router.post("/logout", status_code=204)
async def logout(data: RefreshRequest, session: SessionDep) -> None:
    token_in_db = session.exec(
        select(RefreshToken).where(RefreshToken.token == data.refresh_token)
    ).first()
    if token_in_db:
        session.delete(token_in_db)
        session.commit()
