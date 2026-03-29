from datetime import datetime
from pydantic import BaseModel


class UserTotalBalance(BaseModel):
    amount: float
    currency: str
    period_from: datetime
    period_to: datetime


class UserTotalIncome(BaseModel):
    amount: float
    currency: str
    period_from: datetime
    period_to: datetime


class UserTotalExpense(BaseModel):
    amount: float
    currency: str
    period_from: datetime
    period_to: datetime
