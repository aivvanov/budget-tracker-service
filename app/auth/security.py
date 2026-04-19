from datetime import timedelta, datetime, timezone
import os
import jwt
from dotenv import load_dotenv
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from .schemas import Token, RefreshRequest

load_dotenv()

ACCESS_SECRET_KEY = os.getenv("ACCESS_SECRET_KEY")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
REFRESH_TOKEN_EXPIRE_MINUTES = os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/login")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Get a jwt access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, ACCESS_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    """Get a refresh token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=7))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_refresh_token_payload(data: RefreshRequest) -> dict:
    """Validate refresh token"""
    try:
        payload = jwt.decode(
            data.refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM]
        )
        return payload
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=403, detail="Invalid refresh token") from exc
