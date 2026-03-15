from datetime import datetime
from fastapi import HTTPException
from sqlmodel import select
from app.db.session import SessionDep
from app.models.account import Account

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
