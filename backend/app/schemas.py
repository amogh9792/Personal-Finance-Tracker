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
    category_id: int       # use FK instead of text
    description: Optional[str] = None


class TransactionOut(BaseModel):
    id: int
    date: datetime
    amount: float
    category_id: int
    category_name: Optional[str] = None  # join with categories.name
    description: Optional[str] = None
    owner_id: int

    class Config:
        orm_mode = True


class CategoryCreate(BaseModel):
    name: str


class CategoryOut(BaseModel):
    id: int
    name: str
    user_id: int

    class Config:
        orm_mode = True