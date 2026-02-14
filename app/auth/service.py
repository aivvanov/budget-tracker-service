from pwdlib import PasswordHash
from sqlmodel import select
from app.schemas.user import UserInDB
from app.db.session import SessionDep
from app.models.user import User


password_hash = PasswordHash.recommended()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify user's password"""
    return password_hash.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Hash user's password"""
    return password_hash.hash(password)


def get_user(session: SessionDep, email: str) -> User | None:
    """Get a user from database by email"""
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()
    return user

def get_user_by_username(session: SessionDep, username: str) -> User | None:
    """Get a user from database by username"""
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    return user

def authenticate_user(session: SessionDep, username: str, password: str) -> User | None:
    """Authenticate user using his password"""
    user = get_user_by_username(session, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
