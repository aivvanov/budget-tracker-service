from pydantic import BaseModel

class BaseDependancies:
    def __init__(self, x_system_id: str | None = None):
        self.x_system_id = x_system_id

class CommonQueryParams:
    def __init__(self, q: str | None = None, offset: int = 0, limit: int = 10):
        self.q = q
        self.offset = offset
        self.limit = limit

class CommonHeaders(BaseModel):
    host: str
    save_data: bool
    if_modified_since: str | None = None
    traceparent: str | None = None
    x_tag: list[str] = []
