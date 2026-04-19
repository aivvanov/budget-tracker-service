from app.models.user import User
from app.models.account import Account
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.exchange_rate import ExchangeRate
from sqlmodel import SQLModel, create_engine
from . import session


def init_db():
    # Create engine after all models are registered
    session.engine = create_engine(
        session.SQLITE_URL, connect_args=session.connect_args
    )
    # Create all tables
    SQLModel.metadata.create_all(session.engine)
