from datetime import date
from pydantic import BaseModel, EmailStr, Field


class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class TransactionIn(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    amount: float = Field(gt=0)
    type: str = Field(pattern="^(income|expense)$")
    category: str = Field(min_length=1, max_length=80)
    note: str = Field(default="", max_length=500)
    date: date

class TransactionOut(TransactionIn):
    id: int
    class Config:
        from_attributes = True


class BudgetIn(BaseModel):
    category: str = Field(min_length=1, max_length=80)
    monthly_limit: float = Field(gt=0)
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=2000, le=2100)

class BudgetOut(BudgetIn):
    id: int
    class Config:
        from_attributes = True
