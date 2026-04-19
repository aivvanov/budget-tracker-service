import json
from typing import Annotated
from datetime import datetime, timezone
from fastapi import APIRouter, Query, Depends
from app.db.session import SessionDep
from app.auth.security import oauth2_scheme
from app.auth.dependencies import get_current_user_id
from app.services.transaction import get_user_total_income_in_default_currency
from app.services.user import get_curr_user_default_currency
from app.services.account import get_user_total_balance_in_default_currency
from app.schemas.analytics import UserTotalBalance, UserTotalExpense, UserTotalIncome
from app.core.dependencies.dep import CommonQueryParams

router = APIRouter(prefix="/v1/analytics", tags=["analytics"])


@router.get("/current_balance", summary="Get user's balance in their default currency")
async def get_user_current_balance(
    commons: Annotated[CommonQueryParams, Depends(CommonQueryParams)],
    session: SessionDep,
    token: Annotated[str, Depends(oauth2_scheme)],
    user_id: Annotated[str, Depends(get_current_user_id)],
    default_currency: Annotated[str, Depends(get_curr_user_default_currency)],
) -> UserTotalBalance:

    # Get a user's total balance in their default currency
    total_balance = get_user_total_balance_in_default_currency(
        session, user_id, default_currency
    )

    result = UserTotalBalance(
        amount=round(total_balance, 2),
        currency=default_currency,
        period_from=commons.date_from,
        period_to=commons.date_to,
    )

    return result


@router.get("/total_income", summary="Get total income in user's default currency")
async def get_user_total_income(
    session: SessionDep,
    token: Annotated[str, Depends(oauth2_scheme)],
    user_id: Annotated[str, Depends(get_current_user_id)],
    default_currency: Annotated[str, Depends(get_curr_user_default_currency)],
    date_from: datetime = Query(default=None),
    date_to: datetime = Query(default=None),
) -> UserTotalIncome:

    # In case the input date's filers are None, set a default period as a current month
    now = datetime.now(timezone.utc)
    date_from = date_from or now.replace(day=1, hour=0, minute=0, second=0)
    date_to = date_to or now

    # Get user's total income in their default currency
    income = get_user_total_income_in_default_currency(
        session, user_id, default_currency, True, date_from, date_to
    )

    result = UserTotalIncome(
        amount=round(income, 2),
        currency=default_currency,
        period_from=date_from,
        period_to=date_to,
    )

    return result


@router.get("/total_expense", summary="Get total expense in user's default currency")
async def get_user_total_expense(
    session: SessionDep,
    token: Annotated[str, Depends(oauth2_scheme)],
    user_id: Annotated[str, Depends(get_current_user_id)],
    default_currency: Annotated[str, Depends(get_curr_user_default_currency)],
    date_from: datetime = Query(default=None),
    date_to: datetime = Query(default=None),
) -> UserTotalExpense:

    # In case the input date's filers are None, set a default period as a current month
    now = datetime.now(timezone.utc)
    date_from = date_from or now.replace(day=1, hour=0, minute=0, second=0)
    date_to = date_to or now

    # Get user's total expense in their default currency
    expense = get_user_total_income_in_default_currency(
        session, user_id, default_currency, False, date_from, date_to
    )

    result = UserTotalExpense(
        amount=round(expense, 2),
        # amount=expense,
        currency=default_currency,
        period_from=date_from,
        period_to=date_to,
    )

    return result
