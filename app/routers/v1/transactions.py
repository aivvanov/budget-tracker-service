from typing import Annotated
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlmodel import select, func
from app.models.transaction import Transaction
from app.models.category import Category
from app.schemas.transaction import TransactionResponse, TransactionCreate, TransactionSummary
from app.schemas.transaction import TransactionUpdate, TransactionDeleteResponse
from app.core.dependencies.dep import CommonQueryParams
from app.db.session import SessionDep
from app.auth.security import oauth2_scheme
from app.auth.dependencies import get_current_user_id
from app.models.account import Account
from app.services.transaction import change_acc_balance

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


# TO DO: Add default user's currency and do summarizing by it
@router.get('/summary')
async def get_trx_summary(
    session: SessionDep,
    token: Annotated[str, Depends(oauth2_scheme)],
    user_id: Annotated[str, Depends(get_current_user_id)],
    currency: str = Query(default="USD"), # TO DO Depends(get_current_user_default_curr)
    date_from: datetime = Query(default=None),
    date_to: datetime = Query(default=None),
) -> TransactionSummary:

    # Default piriod of time is current month
    now = datetime.now(timezone.utc)
    date_from = date_from or now.replace(day=1, hour=0, minute=0, second=0)
    date_to = date_to or now

    # Base filter
    base_filter = [
        Transaction.user_id == user_id,
        Transaction.currency == currency, # TO DO: Get all transactions
        Transaction.created_at >= date_from,
        Transaction.created_at <= date_to
    ]

    # TO DO: Convert all trx currencies to default currency rate

    income = session.exec(
        select(func.sum(Transaction.amount))
        .join(Category, Transaction.category_id == Category.id)
        .where(*base_filter, Category.is_income == True)
    ).one_or_none() or 0.0

    expense = session.exec(
        select(func.sum(Transaction.amount))
        .join(Category, Transaction.category_id == Category.id)
        .where(*base_filter, Category.is_income == False)
    ).one_or_none() or 0.0

    db_trx_summary = TransactionSummary(
        total_income=income,
        total_expense=expense,
        currency=currency,
        period_from=date_from,
        period_to=date_to,
    )

    return db_trx_summary

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
        select(Account)
        .where(
            Account.id == transaction.account_id,
            Account.user_id == user_id
        )
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    current_acc_balance = await change_acc_balance(transaction.account_id, transaction.amount, category.is_income, session)
    if not current_acc_balance:
        raise HTTPException(status_code=404, detail="Could not withdraw the input from the account")

    db_transaction = Transaction(
        amount=transaction.amount,
        currency=account.currency,
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
