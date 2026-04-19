from pydantic import BaseModel
from datetime import datetime, timezone


class BaseDependancies:
    def __init__(self, x_system_id: str | None = None):
        self.x_system_id = x_system_id


class CommonQueryParams:
    def __init__(
        self,
        offset: int = 0,
        limit: int = 10,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ):
        self.offset = offset
        self.limit = limit
        now = datetime.now(timezone.utc)
        self.date_from = date_from or now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        self.date_to = date_to or now


class CommonHeaders(BaseModel):
    host: str
    save_data: bool
    if_modified_since: str | None = None
    traceparent: str | None = None
    x_tag: list[str] = []
