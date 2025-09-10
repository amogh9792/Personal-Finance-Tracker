from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# User schemas
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

# Transaction schemas
class TransactionCreate(BaseModel):
    amount: float
    category: str   # "Income" or "Expense"
    description: Optional[str] = None

class TransactionOut(TransactionCreate):
    id: int
    date: datetime
    owner_id: int
