import json
from sqlmodel import select
from app.models.account import Account
from app.schemas.account import AccountResponse
from app.services.exchange_rate import convert_currency


def get_user_accounts(session, user_id, offset=0, limit=None) -> list[AccountResponse]:
    """Get user accounts by user_id"""
    query = select(Account).where(Account.user_id == user_id).offset(offset)
    if limit is not None:
        query = query.limit(limit)

    accounts = session.exec(query).all()

    return [t.model_dump(mode="json") for t in accounts]


def get_user_total_balance_in_default_currency(
    session, user_id, default_currency
) -> float | None:
    """Calculate the total balance in the user's default currency"""

    accounts = get_user_accounts(session, user_id)

    total = 0.0
    for acc in accounts:
        curr_amount = convert_currency(
            session, acc["amount"], acc["currency"], default_currency
        )
        total += curr_amount

    return total
