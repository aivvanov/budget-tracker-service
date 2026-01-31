from pwdlib import PasswordHash
from .schemas import UserInDB

password_hash = PasswordHash.recommended()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify user's password"""
    return password_hash.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Hash user's password"""
    return password_hash.hash(password)


def get_user(db, username: str):
    """Get a users from database"""
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def authenticate_user(db, username: str, password: str) -> UserInDB | None:
    """Authenticate user using his password"""
    user = get_user(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
