from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from app.core.scheduler import start_scheduler, scheduler, job_fetch_rates
from .db.init_db import init_db
from .core.middleware import add_process_time_header, setup_cors
from .core.dependencies.validation import ValidationException
from .core.dependencies.handlers import validation_exception_handler
from .core.dependencies.dep import BaseDependancies
from .auth import routes
from .routers.v1 import transactions, categories, users, accounts, currency

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Launch the scheduler at startup
    start_scheduler()

    # Fetch rates straight away
    await job_fetch_rates()

    yield  # App is running

    # When app stopped, we stop the scheduler
    scheduler.shutdown()
    print("[scheduler] stopped")

app = FastAPI(lifespan=lifespan, dependencies=[Depends(BaseDependancies)])

app.middleware("http")(add_process_time_header)
setup_cors(app)

@app.on_event("startup")
def on_startup():
    """Initialize database on app startup."""
    init_db()

app.add_exception_handler(ValidationException, validation_exception_handler)

app.include_router(routes.router)
app.include_router(transactions.router)
app.include_router(categories.router)
app.include_router(users.router)
app.include_router(accounts.router)
app.include_router(currency.router)
