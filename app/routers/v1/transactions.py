from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlmodel import select
from app.models.transaction import TransactionBase, Transaction, UpdateTransaction
from app.core.dependencies.dep import CommonQueryParams
from app.db.session import SessionDep


router = APIRouter(
    prefix="/transactions",
    tags=["transactions"]
)


@router.get('/',
        summary="The method that returns all stored transactions from database.",
        description="Get all transaction."
        )
async def get_transactions(commons: Annotated[CommonQueryParams, Depends(CommonQueryParams)],
                            #token: Annotated[str, Depends(oauth2_scheme)],
                            session: SessionDep
                        ) -> list[Transaction]:
    return session.exec(select(Transaction).offset(commons.offset).limit(commons.limit)).all()

@router.get('/{trx_id}')
async def get_transaction(trx_id: Annotated[str, Path(title='The ID of the transaction to get')],
                        session: SessionDep,
                        #token: Annotated[str, Depends(oauth2_scheme)]
                    ) -> Transaction:
    transaction = session.get(Transaction, trx_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.delete("/{trx_id}")
async def delete_transaction(trx_id: int, 
                            session: SessionDep,
                            #token: Annotated[str, Depends(oauth2_scheme)]
                        ):
    transaction = session.get(Transaction, trx_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    session.delete(transaction)
    session.commit()
    return {"deleted": True}


@router.post('/', status_code=status.HTTP_201_CREATED)
async def add_transaction(transaction: TransactionBase, 
                        session: SessionDep,
                        #token: Annotated[str, Depends(oauth2_scheme)]
                    ) -> Transaction:
    db_transaction = Transaction.from_orm(transaction)

    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)
    return db_transaction

# to fix
@router.patch('/{trx_id}', response_model=Transaction)
async def update_transaction(trx_id: str, trx: UpdateTransaction, 
                            session: SessionDep,
                            #token: Annotated[str, Depends(oauth2_scheme)]
                        ):
    trx_db = session.get(Transaction, trx_id)
    if not trx_db:
        raise HTTPException(status_code=404, detail="Transaction not found")

    trx_data = trx.model_dump(exclude_unset=True, exclude_none=True)
    trx_db.sqlmodel_update(trx_data)
    session.add(trx_db)
    session.commit()
    session.refresh(trx_db)
    return trx_db
