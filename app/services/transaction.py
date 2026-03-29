from datetime import datetime
from fastapi import HTTPException
from sqlmodel import select
from app.db.session import SessionDep
from app.models.account import Account
from app.schemas.transaction import TransactionResponse
from app.models.transaction import Transaction
from app.models.category import Category
from app.services.exchange_rate import convert_currency


def get_user_transactions(
    session: SessionDep,
    user_id: str,
    is_income: bool = None,
    offset: int = 0,
    limit: int = None,
    date_from: datetime = None,
    date_to: datetime = None
) -> list[TransactionResponse]:
    transactions = session.exec(
        select(Transaction)
        .join(Category, Transaction.category_id == Category.id)
        .where(Transaction.user_id == user_id,
            Transaction.created_at >= date_from,
            Transaction.created_at <= date_to,
            Category.is_income == is_income
        )
        .offset(offset)
        .limit(limit)
    ).all()

    return [t.model_dump(mode='json') for t in transactions]


def get_user_total_income_in_default_currency(
    session: SessionDep,
    user_id: str,
    default_currency: str,
    is_income: bool = None,
    date_from: datetime = None,
    date_to: datetime = None
) -> float | None:
    """Calculate the total income in the user's default currency"""

    transactions = get_user_transactions(session, user_id, is_income, 0, None, date_from, date_to)

    total = 0.0
    for trx in transactions:
        curr_amount = convert_currency(session, trx["amount"], trx["currency"], default_currency)
        total += curr_amount

    return total


async def change_acc_balance(
    account_id: str,
    amount: float,
    is_income: bool,
    session: SessionDep
):
    account = session.exec(
        select(Account)
        .where(
            Account.id == account_id)
        ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    if not is_income:
        account.amount -= amount
    else:
        account.amount += amount
    account.updated_at = datetime.utcnow()

    session.add(account)
    session.commit()
    session.refresh(account)

    return account