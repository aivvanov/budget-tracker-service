from datetime import datetime
from fastapi import HTTPException, Path
from typing import Annotated
from sqlmodel import select
from app.db.session import SessionDep
from app.models.account import Account
from app.models.transfer import Transfer
from app.services.transaction import change_acc_balance
from app.schemas.transaction import TransactionResponse
from app.models.transaction import Transaction
from app.models.category import Category
from app.services.exchange_rate import convert_currency


async def cancel_transfer(id: Annotated[int, Path], session: SessionDep):
    transfer = session.exec(select(Transfer).where(Transfer.id == id)).first()

    try:
        await change_acc_balance(transfer.from_account_id, transfer.amount, True, session)
        await change_acc_balance(transfer.to_account_id, transfer.amount_to, False, session)
        session.delete(transfer)
        session.commit()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Error occurred while deleting a transfer",
        ) from exc

    return transfer
