from typing import Annotated
from sqlmodel import Session
from fastapi import Depends

SQLITE_FILE_NAME = "database.db"
SQLITE_URL = f"sqlite:///{SQLITE_FILE_NAME}"

connect_args = {"check_same_thread": False}

# Engine is created in init_db.py to ensure all models are registered first
engine = None


def get_session():
    """Dependency to get SQLAlchemy db session."""
    if engine is None:
        raise RuntimeError("Database engine not initialized. Call init_db() first.")
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
