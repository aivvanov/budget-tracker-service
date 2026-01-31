from typing import Annotated
from sqlmodel import Session, create_engine
from fastapi import Depends


SQLITE_FILE_NAME = "database.db"
SQLITE_URL = f"sqlite:///{SQLITE_FILE_NAME}"
print(f"DEBUG: SQLITE_FILE_NAME='{SQLITE_FILE_NAME}'")

connect_args = {"check_same_thread": False}
engine = create_engine(SQLITE_URL, connect_args=connect_args)


def get_session():
    """Dependency to get SQLAlchemy db session."""
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
