from typing import Annotated
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlmodel import select
from app.auth.security import oauth2_scheme
from app.db.session import SessionDep
from app.core.dependencies.dep import CommonQueryParams
from app.schemas.account import AccountResponse, AccountCreate, AccountUpdate, AccountDeleteResponse
from app.auth.dependencies import get_current_user_id
from app.models.account import Account

router = APIRouter(
    prefix="/v1/accounts",
    tags=["accounts"]
)

@router.get('/')
async def get_accounts(
    commons: Annotated[CommonQueryParams, Depends(CommonQueryParams)],
    token: Annotated[str, Depends(oauth2_scheme)],
    session: SessionDep,
    user_id: Annotated[str, Depends(get_current_user_id)]
) -> list[AccountResponse]:
    return session.exec(
        select(Account)
        .where(Account.user_id == user_id)
        .offset(commons.offset)
        .limit(commons.limit)
    ).all()

@router.get('/{id}')
async def get_account(
    id: Annotated[str, Path(title='The ID of the transaction to get')],
    session: SessionDep,
    token: Annotated[str, Depends(oauth2_scheme)],
    user_id: Annotated[str, Depends(get_current_user_id)]
) -> AccountResponse:

    account = session.exec(
        select(Account)
        .where(
            Account.id == id,
            Account.user_id == user_id
        )
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    return account

@router.post(
    '/', 
    status_code=status.HTTP_201_CREATED
)
async def add_account(
    account: AccountCreate,
    session: SessionDep,
    token: Annotated[str, Depends(oauth2_scheme)],
    user_id: Annotated[str, Depends(get_current_user_id)]
) -> AccountResponse:

    db_account = Account(
        
        name=account.name,
        amount=account.amount,
        currency=account.currency,
        icon_url=account.icon_url,
        user_id=user_id,
        created_at=datetime.now(timezone.utc),
        updated_at=None
    )

    session.add(db_account)
    session.commit()
    session.refresh(db_account)

    return db_account

@router.patch('/{id}')
async def update_account(
    id: Annotated[str, Path],
    account: AccountUpdate,
    session: SessionDep,
    token: Annotated[str, Depends(oauth2_scheme)],
    user_id: Annotated[str, Depends(get_current_user_id)]
) -> AccountResponse:

    account_db = session.exec(
        select(Account)
        .where(
            Account.id == id,
            Account.user_id == user_id
        )
    ).first()
    if not account_db:
        raise HTTPException(status_code=404, detail="Account not found")

    account_data = account.model_dump(exclude_unset=True, exclude=None)
    account_db.updated_at = datetime.now(timezone.utc)
    account_db.sqlmodel_update(account_data)

    session.add(account_db)
    session.commit()
    session.refresh(account_db)

    return account_db

@router.delete("/{id}")
async def delete_account(
    id: Annotated[int, Path],
    session: SessionDep,
    token: Annotated[str, Depends(oauth2_scheme)],
    user_id: Annotated[str, Depends(get_current_user_id)]
) -> AccountDeleteResponse:

    account = session.exec(
        select(Account)
        .where(
            Account.id == id,
            Account.user_id == user_id
        )
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    session.delete(account)
    session.commit()

    return AccountDeleteResponse(id=id)
