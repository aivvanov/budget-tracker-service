from datetime import datetime
import httpx
from sqlmodel import select
from sqlalchemy import text
from app.models.exchange_rate import ExchangeRate
from app.db.session import SessionDep

BASE_CURRENCY = "USD"
EXCHANGE_RATE_API_URL = "https://api.frankfurter.dev/v1/latest"


async def fetch_and_save_rates(session: SessionDep):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            EXCHANGE_RATE_API_URL, params={"from": BASE_CURRENCY}, timeout=10.0
        )
        response.raise_for_status()
        data = response.json()

    fetched_at = datetime.utcnow()

    for to_currency, rate in data["rates"].items():
        record = ExchangeRate(
            from_currency=BASE_CURRENCY,
            to_currency=to_currency,
            rate=rate,
            fetched_at=fetched_at,
        )
        session.add(record)

    session.commit()
    print(f"[scheduler] Rates has been updated: {fetched_at}")


def get_latest_rate(
    session: SessionDep, from_currency: str, to_currency: str
) -> float | None:
    statement = (
        select(ExchangeRate)
        .where(
            ExchangeRate.from_currency == from_currency,
            ExchangeRate.to_currency == to_currency,
        )
        .order_by(text("fetched_at DESC"))
    )
    record = session.exec(statement).first()
    return record.rate if record else None


def get_currency_from_db(currency, session: SessionDep) -> str:

    if currency == BASE_CURRENCY:
        return BASE_CURRENCY

    rate = session.exec(
        select(ExchangeRate).where(ExchangeRate.to_currency == currency)
    ).first()
    return rate


def convert_currency(
    session: SessionDep, amount: float, from_currency: str, to_currency: str
) -> float | None:

    if from_currency == to_currency:
        return amount

    rate = get_latest_rate(session, from_currency, to_currency)
    return amount * rate if rate else None
