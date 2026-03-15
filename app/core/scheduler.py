from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlmodel import Session
from app.db.session import engine
from app.services.exchange_rate import fetch_and_save_rates

scheduler = AsyncIOScheduler()

async def job_fetch_rates():
    with Session(engine) as session:
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
