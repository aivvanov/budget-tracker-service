from fastapi import FastAPI, Query, Path, Body, Cookie, Header, status, HTTPException, Form, UploadFile, File, Response, Request, Depends, dependencies
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import Annotated, Any
from models import BaseTransaction, UpdateTransaction, TransactionOut, Category, CategoriesFilterParams, CommonHeaders, FormDataIn, FormDataOut, mock_transactions, CommonQueryParams, BaseDependancies, User, UserInDB, mock_users
from auth import oauth2_scheme, get_curr_user, get_curr_active_user, OAuth2PasswordRequestForm, fake_hash_password

app = FastAPI(dependencies=[Depends(BaseDependancies)])

class ValidationException(Exception):
    def __init__(self, field: str, min_length: int):
        self.field = field
        self.min_length = min_length

# async def common_parameters(q: str | None = None, skip: Annotated[int, Query(deprecated = True, title = 'Offset of lost')] = 0, limit: int = 10):
#    return {"q": q, "skip": skip, "limit": limit}

# CommonsDep = Annotated[dict, Depends(common_parameters)]


@app.exception_handler(ValidationException)
async def unicorn_exception_handler(request: Request, exc: ValidationException):
    return JSONResponse(
        status_code=406,
        content={"detail":f"The field '{exc.field}' must be longer than {exc.min_length} characters"},
    )


@app.get('/transactions', 
        tags=["transactions"],
        summary="Get transactions",
        description="Get all transaction"
        )
async def get_transactions(commons: Annotated[CommonQueryParams, Depends(CommonQueryParams)],
                            token: Annotated[str, Depends(oauth2_scheme)]
                           ) -> list[TransactionOut]:
    return mock_transactions[commons.offset : commons.offset + commons.limit]


@app.get('/transactions/{trx_id}', tags=["transactions"])
async def get_transaction(trx_id: Annotated[str, Path(title='The ID of the transaction to get')]) -> TransactionOut:
    for trx in mock_transactions:
        trx_dump = jsonable_encoder(trx)
        if trx_dump["id"] == trx_id:
            return trx
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Transaction not found")


@app.post('/transactions', status_code=status.HTTP_201_CREATED, tags=["transactions"])
async def add_transaction(transaction: BaseTransaction) -> TransactionOut:
    #trx = transaction.model_dump()
    #rx.update({"id": uuid.uuid4()})
    return transaction


@app.put('/transactions/{trx_id}', response_model=TransactionOut, tags=["transactions"])
async def update_transaction(trx_id: str, trx: BaseTransaction):
    for i, existing in enumerate(mock_transactions):
        if existing.id == trx_id:
            mock_transactions[i] = trx
            return trx

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Transaction {trx_id} not found"
    )


@app.patch("/transactions/{trx_id}", response_model=TransactionOut, tags=["transactions"])
async def update_item(trx_id: str, trx: UpdateTransaction):
    index = next((i for i, t in enumerate(mock_transactions) if t["id"] == trx_id), None)

    if index is None:
        raise HTTPException(status_code=404, detail=f"Transaction {trx_id} not found")

    stored_trx_data = mock_transactions[index]
    stored_item_model = TransactionOut(**stored_trx_data)

    update_data = trx.model_dump(exclude_unset=True)
    updated_item = stored_item_model.model_copy(update=update_data)
    mock_transactions[index] = jsonable_encoder(updated_item)
    return updated_item


@app.get('/categories', tags=["categories"])
async def get_category(filter_query: Annotated[CategoriesFilterParams, Query()],
                          headers: Annotated[CommonHeaders, Header()],
                          commons: Annotated[CommonQueryParams, Depends(CommonQueryParams)],
                          ads_id: Annotated[str | None, Cookie()] = None
                          ):
    return headers


@app.post('/categories', status_code=status.HTTP_201_CREATED, tags=["categories"])
async def create_category(category: Category, importance: Annotated[int | None, Body(ge=0, le=10)] = None):
    result = category.model_dump()
    if importance:
        result.update({"importance": importance})
    return result


# @app.post("/login", tags=["auth"])
# async def login(data: Annotated[FormDataIn, Form()]) -> FormDataOut:
#     creds = data.model_dump()

#     validation_rules = {
#         "username": 3,
#         "password": 10
#     }

#     for field, min_len in validation_rules.items():
#         if len(creds[field]) <= min_len:
#             raise ValidationException(field, min_len)

#     return FormDataOut(username=data.username)


@app.post("/file", tags=["files"])
async def upload_file(file: Annotated[UploadFile, File()]):
    content = await file.read()
    return Response(content=content, media_type="application/octet-stream")


@app.get("/users/me",  tags=["auth"])
async def read_users_me(
    current_user: Annotated[User, Depends(get_curr_active_user)],
):
    return current_user


@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = mock_users.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}