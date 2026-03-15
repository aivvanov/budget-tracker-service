from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from app.db.session import SessionDep
from app.auth.security import oauth2_scheme
from app.auth.dependencies import get_current_user_id
from app.services.exchange_rate import fetch_and_save_rates, get_latest_rate
from app.schemas.currency import RatesRefreshResponse, RatesResponse

router = APIRouter(prefix="/v1/rates", tags=["currencies"])

@router.post("/refresh")
async def refresh_rates(
    session: SessionDep,
    token: Annotated[str, Depends(oauth2_scheme)],
    user_id: Annotated[str, Depends(get_current_user_id)]
) -> RatesRefreshResponse:
    await fetch_and_save_rates(session)
    return RatesRefreshResponse(status = "success")

@router.get("/")
def get_rate(
    from_currency: str = "USD",
    to_currency: str = "EUR",
    session: SessionDep = None,
    token: Annotated[str, Depends(oauth2_scheme)] = None,
    user_id: Annotated[str, Depends(get_current_user_id)] = None
) -> RatesResponse:
    rate = get_latest_rate(session, from_currency, to_currency)
    if not rate:
        raise HTTPException(status_code=404, detail="Курс не найден")

    return RatesResponse(from_currency = from_currency, to_currency = to_currency, rate = rate)
