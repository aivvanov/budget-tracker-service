from typing import Annotated
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlmodel import select
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionResponse, TransactionCreate
from app.schemas.transaction import TransactionUpdate, TransactionDeleteResponse
from app.core.dependencies.dep import CommonQueryParams
from app.db.session import SessionDep
from app.auth.security import oauth2_scheme


router = APIRouter(
    prefix="/transactions",
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
    session: SessionDep
) -> list[TransactionResponse]:
    return session.exec(
        select(Transaction)
        .offset(commons.offset)
        .limit(commons.limit)
    ).all()

@router.get('/{trx_id}')
async def get_transaction(
    trx_id: Annotated[str, Path(title='The ID of the transaction to get')],
    session: SessionDep,
    token: Annotated[str, Depends(oauth2_scheme)]
) -> TransactionResponse:
    transaction = session.get(Transaction, trx_id)
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
    token: Annotated[str, Depends(oauth2_scheme)]
) -> TransactionResponse:
    db_transaction = Transaction.from_orm(transaction)
    db_transaction.created_at = datetime.now(timezone.utc)
    db_transaction.updated_at = None

    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)

    return db_transaction

@router.patch('/{trx_id}')
async def update_transaction(
    trx_id: str, trx: TransactionUpdate,
    session: SessionDep,
    token: Annotated[str, Depends(oauth2_scheme)]
) -> TransactionResponse:
    trx_db = session.get(Transaction, trx_id)
    if not trx_db:
        raise HTTPException(status_code=404, detail="Transaction not found")

    trx_data = trx.model_dump(exclude_unset=True, exclude=None)
    trx_db.updated_at = datetime.now(timezone.utc)
    trx_db.sqlmodel_update(trx_data)

    session.add(trx_db)
    session.commit()
    session.refresh(trx_db)

    return trx_db

@router.delete("/{trx_id}")
async def delete_transaction(
    trx_id: int,
    session: SessionDep,
    token: Annotated[str, Depends(oauth2_scheme)]
) -> TransactionDeleteResponse:
    transaction = session.get(Transaction, trx_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    session.delete(transaction)
    session.commit()

    return TransactionDeleteResponse(trx_id=trx_id)
