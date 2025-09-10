from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from app.db import get_cursor
from app import schemas
from app.core.security import decode_access_token
from app.core.exceptions import AppException
from app.utils.logger import logger

router = APIRouter(prefix="/transactions", tags=["transactions"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise AppException("Invalid or expired token", 401)
    return payload["sub"]

# Add a new transaction
@router.post("/", response_model=schemas.TransactionOut)
def create_transaction(txn: schemas.TransactionCreate, username: str = Depends(get_current_user)):
    with get_cursor() as cur:
        # find user id
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        if not user:
            raise AppException("User not found", 404)

        cur.execute(
            """
            INSERT INTO transactions (amount, category, description, owner_id)
            VALUES (%s, %s, %s, %s) RETURNING id, date, amount, category, description, owner_id
            """,
            (txn.amount, txn.category, txn.description, user["id"]),
        )
        new_txn = cur.fetchone()
        logger.info(f"✅ Transaction added by {username}: {txn.amount} {txn.category}")
        return new_txn

# Get all transactions
@router.get("/", response_model=list[schemas.TransactionOut])
def get_transactions(username: str = Depends(get_current_user)):
    with get_cursor() as cur:
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        if not user:
            raise AppException("User not found", 404)

        cur.execute("SELECT * FROM transactions WHERE owner_id = %s ORDER BY date DESC", (user["id"],))
        rows = cur.fetchall()
        return rows

# Summary API
@router.get("/summary")
def get_summary(username: str = Depends(get_current_user)):
    with get_cursor() as cur:
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        if not user:
            raise AppException("User not found", 404)

        cur.execute("SELECT COALESCE(SUM(amount),0) FROM transactions WHERE owner_id=%s AND category='Income'", (user["id"],))
        income = cur.fetchone()["coalesce"]

        cur.execute("SELECT COALESCE(SUM(amount),0) FROM transactions WHERE owner_id=%s AND category='Expense'", (user["id"],))
        expense = cur.fetchone()["coalesce"]

        return {
            "total_income": float(income),
            "total_expense": float(expense),
            "net_savings": float(income - expense)
        }
