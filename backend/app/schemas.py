from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional

# --- Users ---
class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# --- Transactions ---
class TransactionCreate(BaseModel):
    amount: float
    category: str   # must be Income or Expense
    description: Optional[str] = None

    @validator("category")
    def validate_category(cls, v):
        v = v.capitalize()   # normalize "income" → "Income"
        if v not in ["Income", "Expense"]:
            raise ValueError("Category must be 'Income' or 'Expense'")
        return v


class TransactionOut(TransactionCreate):
    id: int
    date: datetime
    owner_id: int
