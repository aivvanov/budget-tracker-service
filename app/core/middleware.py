import time
import json
import os
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware


async def add_process_time_header(request: Request, call_next):
    """Add process time header to input requests"""
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


def setup_cors(app):
    """Set up CORS parameters as allowed hosts, methods etc."""
    hosts_raw = os.getenv("ALLOWED_HOSTS", "[]")
    origins = json.loads(hosts_raw)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Process-Time"], # custom header from add_process_time_header
    )
