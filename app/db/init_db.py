from sqlmodel import SQLModel
from .session import engine

def init_db():
    SQLModel.metadata.create_all(engine)
