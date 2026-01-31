from typing import Annotated
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException, status
from .schemas import mock_users, User, TokenData
from .security import oauth2_scheme
from .security import ALGORITHM, SECRET_KEY
from .service import get_user

async def get_curr_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """Get current user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError as exc:
        raise credentials_exception from exc
    if (get_user(mock_users, username=token_data.username)) is None:
        raise credentials_exception
    return get_user(mock_users, username=token_data.username)


async def get_curr_active_user(current_user: Annotated[User, Depends(get_curr_user)]):
    """Get current active user"""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
