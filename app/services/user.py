from fastapi import Depends
from typing import Annotated
from sqlmodel import select
from app.db.session import SessionDep
from app.models.user import User
from app.auth.dependencies import get_current_user_id


def get_curr_user_default_currency(
    user_id: Annotated[str, Depends(get_current_user_id)],
    session: SessionDep
) -> str | None:
    user = session.exec(
        select(User)
        .where(User.id == user_id)
    ).first()

    return user.default_currency if user else None
