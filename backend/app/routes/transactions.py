import csv
from fastapi import Query
import io
from fastapi import APIRouter, Depends, Path
from fastapi.responses import StreamingResponse
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

# # Get all transactions
# @router.get("/", response_model=list[schemas.TransactionOut])
# def get_transactions(username: str = Depends(get_current_user)):
#     with get_cursor() as cur:
#         cur.execute("SELECT id FROM users WHERE username = %s", (username,))
#         user = cur.fetchone()
#         if not user:
#             raise AppException("User not found", 404)

#         cur.execute("SELECT * FROM transactions WHERE owner_id = %s ORDER BY date DESC", (user["id"],))
#         rows = cur.fetchall()
#         return rows

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


# Update transaction
@router.put("/{txn_id}", response_model=schemas.TransactionOut)
def update_transaction(
    txn_id: int = Path(..., description="Transaction ID"),
    txn: schemas.TransactionCreate = None,
    username: str = Depends(get_current_user)
):
    with get_cursor() as cur:
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        if not user:
            raise AppException("User not found", 404)

        # Ensure transaction belongs to the user
        cur.execute("SELECT * FROM transactions WHERE id = %s AND owner_id = %s", (txn_id, user["id"]))
        existing = cur.fetchone()
        if not existing:
            raise AppException("Transaction not found", 404)

        cur.execute(
            """
            UPDATE transactions
            SET amount=%s, category=%s, description=%s
            WHERE id=%s AND owner_id=%s
            RETURNING id, date, amount, category, description, owner_id
            """,
            (txn.amount, txn.category, txn.description, txn_id, user["id"])
        )
        updated = cur.fetchone()
        logger.info(f"✏️ Transaction {txn_id} updated by {username}")
        return updated

# Delete transaction
@router.delete("/{txn_id}")
def delete_transaction(
    txn_id: int = Path(..., description="Transaction ID"),
    username: str = Depends(get_current_user)
):
    with get_cursor() as cur:
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        if not user:
            raise AppException("User not found", 404)

        # Ensure transaction belongs to the user
        cur.execute("SELECT id FROM transactions WHERE id = %s AND owner_id = %s", (txn_id, user["id"]))
        existing = cur.fetchone()
        if not existing:
            raise AppException("Transaction not found", 404)

        cur.execute("DELETE FROM transactions WHERE id = %s AND owner_id = %s", (txn_id, user["id"]))
        logger.info(f"🗑️ Transaction {txn_id} deleted by {username}")
        return {"message": f"Transaction {txn_id} deleted successfully"}
    
from fastapi.responses import StreamingResponse
import io
import csv

@router.get("/export")
def export_transactions(username: str = Depends(get_current_user)):
    with get_cursor() as cur:
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        if not user:
            raise AppException("User not found", 404)

        cur.execute(
            "SELECT id, date, amount, category, description FROM transactions WHERE owner_id = %s ORDER BY date DESC",
            (user["id"],),
        )
        rows = cur.fetchall()
        if not rows:
            raise AppException("No transactions found", 404)

        # Write CSV into memory buffer
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Date", "Amount", "Category", "Description"])
        for row in rows:
            writer.writerow([row["id"], row["date"], row["amount"], row["category"], row["description"]])

        # Reset buffer position
        output.seek(0)

        filename = f"{username}_transactions.csv"

        # Proper StreamingResponse with filename
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )

# Get transactions with filters & pagination
@router.get("/", response_model=list[schemas.TransactionOut])
def get_transactions(
    username: str = Depends(get_current_user),
    start: str | None = Query(None, description="Start date (YYYY-MM-DD)"),
    end: str | None = Query(None, description="End date (YYYY-MM-DD)"),
    category: str | None = Query(None, description="Filter by category"),
    limit: int = Query(20, ge=1, le=100, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
):
    with get_cursor() as cur:
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        if not user:
            raise AppException("User not found", 404)

        query = "SELECT * FROM transactions WHERE owner_id = %s"
        params = [user["id"]]

        if start:
            query += " AND date >= %s"
            params.append(start)
        if end:
            query += " AND date <= %s"
            params.append(end)
        if category:
            query += " AND category = %s"
            params.append(category.capitalize())

        query += " ORDER BY date DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cur.execute(query, tuple(params))
        rows = cur.fetchall()
        return rows
