from pydantic import BaseModel, Field

class RatesRefreshResponse(BaseModel):
    status: str = Field(default="success")

class RatesResponse(BaseModel):
    from_currency: str
    to_currency: str
    rate: float
