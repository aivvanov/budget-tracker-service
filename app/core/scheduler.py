from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlmodel import Session
from app.db import session as db_session
from app.services.exchange_rate import fetch_and_save_rates

scheduler = AsyncIOScheduler()


async def job_fetch_rates():
    if db_session.engine is None:
        raise RuntimeError("Database engine not initialized yet")
    with Session(db_session.engine) as session:
        try:
            await fetch_and_save_rates(session)
        except Exception as e:
            print(f"[scheduler] Error while getting rates: {e}")


def start_scheduler():
    scheduler.add_job(
        job_fetch_rates,
        trigger=IntervalTrigger(hours=1),
        id="fetch_exchange_rates",
        replace_existing=True,
    )
    scheduler.start()
    print("[scheduler] is running")
