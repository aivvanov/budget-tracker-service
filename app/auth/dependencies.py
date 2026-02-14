from typing import Annotated
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException, status
from sqlmodel import Session
from app.schemas.user import UserBase
from app.db.session import get_session
from .schemas import TokenData
from .security import oauth2_scheme
from .security import ALGORITHM, SECRET_KEY
from .service import get_user

async def get_curr_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[Session, Depends(get_session)]
):
    """Get current user from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except InvalidTokenError as exc:
        raise credentials_exception from exc
    
    user = get_user(session, email)
    if user is None:
        raise credentials_exception
    return user


async def get_curr_active_user(current_user: Annotated[UserBase, Depends(get_curr_user)]):
    """Get current active user"""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
