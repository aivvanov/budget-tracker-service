import json
from typing import Annotated
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlmodel import select
from app.models.transaction import Transaction
from app.models.category import Category
from app.models.transfer import Transfer
from app.schemas.transaction import TransactionResponse, TransactionCreate
from app.schemas.transaction import TransactionUpdate, TransactionDeleteResponse
from app.schemas.transfer import (
    TransferCreate,
    TransferResponse,
    TransferUpdate,
    TransferDeleteResponse,
)
from app.services.exchange_rate import convert_currency
from app.services.account import withdraw_from_account, top_up_account
from app.services.transfer import cancel_transfer
from app.core.dependencies.dep import CommonQueryParams
from app.db.session import SessionDep
from app.auth.security import oauth2_scheme
from app.auth.dependencies import get_current_user_id
from app.models.account import Account
from app.services.transaction import change_acc_balance

router = APIRouter(prefix="/v1/transfers", tags=["transfers"])


@router.get(
    "/",
    summary="The method that returns all stored transfers from database.",
    description="Get all fransfers.",
)
async def get_transfers(
    commons: Annotated[CommonQueryParams, Depends(CommonQueryParams)],
    token: Annotated[str, Depends(oauth2_scheme)],
    session: SessionDep,
    user_id: Annotated[str, Depends(get_current_user_id)],
) -> list[TransferResponse]:
    return session.exec(
        select(Transfer)
        .where(
            Transfer.user_id == user_id,
            Transfer.occurred_at >= commons.date_from,
            Transfer.occurred_at <= commons.date_to,
        )
        .offset(commons.offset)
        .limit(commons.limit)
    ).all()


@router.get("/{id}")
async def get_transfer(
    id: Annotated[str, Path(title="The ID of the transfer to get")],
    session: SessionDep,
    token: Annotated[str, Depends(oauth2_scheme)],
    user_id: Annotated[str, Depends(get_current_user_id)],
) -> TransferResponse:

    transfer = session.exec(
        select(Transfer).where(Transfer.id == id, Transfer.user_id == user_id)
    ).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")

    return transfer


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_transfer(
    transfer: TransferCreate,
    session: SessionDep,
    token: Annotated[str, Depends(oauth2_scheme)],
    user_id: Annotated[str, Depends(get_current_user_id)],
) -> TransferResponse:

    from_account = session.exec(
        select(Account).where(
            Account.id == transfer.from_account_id, Account.user_id == user_id
        )
    ).first()
    if not from_account:
        raise HTTPException(
            status_code=404,
            detail=f"Account {transfer.from_account_id} not found",
        )

    to_account = session.exec(
        select(Account).where(
            Account.id == transfer.to_account_id, Account.user_id == user_id
        )
    ).first()
    if not to_account:
        raise HTTPException(
            status_code=404,
            detail=f"Account {transfer.to_account_id} not found",
        )

    amount_to = transfer.amount
    if from_account.currency != to_account.currency:
        amount_to = convert_currency(
            session, transfer.amount, from_account.currency, to_account.currency
        )

    try:
        withdraw_from_account(session, user_id, from_account.id, transfer.amount)
        top_up_account(session, user_id, to_account.id, amount_to)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Error occurred while transferring",
        ) from exc

    db_transfer = Transfer(
        from_account_id=transfer.from_account_id,
        to_account_id=transfer.to_account_id,
        amount=transfer.amount,
        amount_to=amount_to,
        description=transfer.description,
        user_id=user_id,
        occurred_at=transfer.occurred_at,
    )

    session.add(db_transfer)
    session.commit()
    session.refresh(db_transfer)

    return db_transfer


# TO DO
# @router.patch("/{id}")
# async def update_transfer(
#     id: Annotated[str, Path],
#     transfer: TransferUpdate,
#     session: SessionDep,
#     token: Annotated[str, Depends(oauth2_scheme)],
#     user_id: Annotated[str, Depends(get_current_user_id)],
# ) -> TransferResponse:

#     transfer_db = session.exec(
#         select(Transfer).where(Transfer.id == id, Transfer.user_id == user_id)
#     ).first()
#     if not transfer_db:
#         raise HTTPException(status_code=404, detail="Transfer not found")

#     from_account = session.exec(
#         select(Account).where(
#             Account.id == transfer.from_account_id, Account.user_id == user_id
#         )
#     ).first()
#     if not from_account:
#         raise HTTPException(
#             status_code=404,
#             detail=f"Account {transfer.from_account_id} not found",
#         )

#     to_account = session.exec(
#         select(Account).where(
#             Account.id == transfer.to_account_id, Account.user_id == user_id
#         )
#     ).first()
#     if not to_account:
#         raise HTTPException(
#             status_code=404,
#             detail=f"Account {transfer.to_account_id} not found",
#         )

#     transfer_data = transfer.model_dump(exclude_unset=True, exclude=None)
#     transfer_db.updated_at = datetime.now(timezone.utc)
#     transfer_db.sqlmodel_update(transfer_data)

#     session.add(transfer_db)
#     session.commit()
#     session.refresh(transfer_db)

#     return transfer_db


@router.delete("/{id}")
async def delete_transfer(
    id: Annotated[int, Path],
    session: SessionDep,
    token: Annotated[str, Depends(oauth2_scheme)],
    user_id: Annotated[str, Depends(get_current_user_id)],
) -> TransferDeleteResponse:
    try:
        await cancel_transfer(id, session)
    except HTTPException:
        raise

    return TransferDeleteResponse(id=id)
