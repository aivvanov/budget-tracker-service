from typing import Annotated
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlmodel import select
from app.models.transaction import Transaction
from app.models.category import Category
from app.schemas.transaction import TransactionResponse, TransactionCreate
from app.schemas.transaction import TransactionUpdate, TransactionDeleteResponse
from app.core.dependencies.dep import CommonQueryParams
from app.db.session import SessionDep
from app.auth.security import oauth2_scheme
from app.auth.dependencies import get_current_user_id
from app.models.account import Account


router = APIRouter(
    prefix="/v1/transactions",
    tags=["transactions"]
)


@router.get(
    '/',
    summary="The method that returns all stored transactions from database.",
    description="Get all transaction."
)
async def get_transactions(
    commons: Annotated[CommonQueryParams, Depends(CommonQueryParams)],
    token: Annotated[str, Depends(oauth2_scheme)],
    session: SessionDep,
    user_id: Annotated[str, Depends(get_current_user_id)]
) -> list[TransactionResponse]:
    return session.exec(
        select(Transaction)
        .where(Transaction.user_id == user_id)
        .offset(commons.offset)
        .limit(commons.limit)
    ).all()

@router.get('/{trx_id}')
async def get_transaction(
    trx_id: Annotated[str, Path(title='The ID of the transaction to get')],
    session: SessionDep,
    token: Annotated[str, Depends(oauth2_scheme)],
    user_id: Annotated[str, Depends(get_current_user_id)]
) -> TransactionResponse:

    transaction = session.exec(
        select(Transaction)
        .where(
            Transaction.id == trx_id,
            Transaction.user_id == user_id
        )
    ).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return transaction

@router.post(
    '/', 
    status_code=status.HTTP_201_CREATED
)
async def add_transaction(
    transaction: TransactionCreate,
    session: SessionDep,
    token: Annotated[str, Depends(oauth2_scheme)],
    user_id: Annotated[str, Depends(get_current_user_id)]
) -> TransactionResponse:
    
    category = session.exec(
        select(Category)
        .where(
            Category.id == transaction.category_id,
            Category.user_id == user_id
        )
    ).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    account = session.exec(
        select(Category)
        .where(
            Account.id == transaction.account_id,
            Account.user_id == user_id
        )
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")


    db_transaction = Transaction(
        amount=transaction.amount,
        currency=transaction.currency,
        description=transaction.description,
        category_id=transaction.category_id,
        account_id=transaction.account_id,
        user_id=user_id,
        created_at=datetime.now(timezone.utc),
        updated_at=None
    )

    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)

    return db_transaction

@router.patch('/{trx_id}')
async def update_transaction(
    trx_id: Annotated[str, Path], 
    trx: TransactionUpdate,
    session: SessionDep,
    token: Annotated[str, Depends(oauth2_scheme)],
    user_id: Annotated[str, Depends(get_current_user_id)]
) -> TransactionResponse:

    trx_db = session.exec(
        select(Transaction)
        .where(
            Transaction.id == trx_id,
            Transaction.user_id == user_id
        )
    ).first()
    if not trx_db:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if trx.category_id and not session.get(Category, trx.category_id):
        raise HTTPException(status_code=404, detail="Category not found")

    if trx.account_id and not session.get(Account, trx.account_id):
        raise HTTPException(status_code=404, detail="Account not found")

    trx_data = trx.model_dump(exclude_unset=True, exclude=None)
    trx_db.updated_at = datetime.now(timezone.utc)
    trx_db.sqlmodel_update(trx_data)

    session.add(trx_db)
    session.commit()
    session.refresh(trx_db)

    return trx_db

@router.delete("/{trx_id}")
async def delete_transaction(
    trx_id: Annotated[int, Path],
    session: SessionDep,
    token: Annotated[str, Depends(oauth2_scheme)],
    user_id: Annotated[str, Depends(get_current_user_id)]
) -> TransactionDeleteResponse:

    transaction = session.exec(
        select(Transaction)
        .where(
            Transaction.id == trx_id,
            Transaction.user_id == user_id
        )
    ).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    session.delete(transaction)
    session.commit()

    return TransactionDeleteResponse(trx_id=trx_id)
