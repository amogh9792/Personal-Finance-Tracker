import csv
import io
from fastapi import APIRouter, Depends, Path, Query
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


# ------------------------
# Add a new transaction
# ------------------------
@router.post("/", response_model=schemas.TransactionOut)
def create_transaction(txn: schemas.TransactionCreate, username: str = Depends(get_current_user)):
    with get_cursor() as cur:
        # find user id
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        if not user:
            raise AppException("User not found", 404)

        # ensure category exists
        cur.execute("SELECT id, name FROM categories WHERE id = %s AND user_id = %s", (txn.category_id, user["id"]))
        category = cur.fetchone()
        if not category:
            raise AppException("Invalid category for this user", 400)

        cur.execute(
            """
            INSERT INTO transactions (amount, category_id, description, owner_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id, date, amount, category_id, description, owner_id
            """,
            (txn.amount, txn.category_id, txn.description, user["id"]),
        )
        new_txn = cur.fetchone()
        new_txn["category_name"] = category["name"]

        logger.info(f"✅ Transaction added by {username}: {txn.amount} in {category['name']}")
        return new_txn


# ------------------------
# Summary API
# ------------------------
@router.get("/summary")
def get_summary(username: str = Depends(get_current_user)):
    with get_cursor() as cur:
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        if not user:
            raise AppException("User not found", 404)

        cur.execute("""
            SELECT COALESCE(SUM(amount),0) as income
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.owner_id=%s AND c.name='Income'
        """, (user["id"],))
        income = cur.fetchone()["income"]

        cur.execute("""
            SELECT COALESCE(SUM(amount),0) as expense
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.owner_id=%s AND c.name='Expense'
        """, (user["id"],))
        expense = cur.fetchone()["expense"]

        return {
            "total_income": float(income or 0),
            "total_expense": float(expense or 0),
            "net_savings": float((income or 0) - (expense or 0))
        }


# ------------------------
# Update transaction
# ------------------------
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

        # ensure transaction exists
        cur.execute("SELECT * FROM transactions WHERE id = %s AND owner_id = %s", (txn_id, user["id"]))
        existing = cur.fetchone()
        if not existing:
            raise AppException("Transaction not found", 404)

        # ensure category exists
        cur.execute("SELECT id, name FROM categories WHERE id = %s AND user_id = %s", (txn.category_id, user["id"]))
        category = cur.fetchone()
        if not category:
            raise AppException("Invalid category for this user", 400)

        cur.execute(
            """
            UPDATE transactions
            SET amount=%s, category_id=%s, description=%s
            WHERE id=%s AND owner_id=%s
            RETURNING id, date, amount, category_id, description, owner_id
            """,
            (txn.amount, txn.category_id, txn.description, txn_id, user["id"])
        )
        updated = cur.fetchone()
        updated["category_name"] = category["name"]

        logger.info(f"✏️ Transaction {txn_id} updated by {username}")
        return updated


# ------------------------
# Delete transaction
# ------------------------
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

        cur.execute("SELECT id FROM transactions WHERE id = %s AND owner_id = %s", (txn_id, user["id"]))
        existing = cur.fetchone()
        if not existing:
            raise AppException("Transaction not found", 404)

        cur.execute("DELETE FROM transactions WHERE id = %s AND owner_id = %s", (txn_id, user["id"]))
        logger.info(f"🗑️ Transaction {txn_id} deleted by {username}")
        return {"message": f"Transaction {txn_id} deleted successfully"}


# ------------------------
# Export CSV
# ------------------------
@router.get("/export")
def export_transactions(username: str = Depends(get_current_user)):
    with get_cursor() as cur:
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        if not user:
            raise AppException("User not found", 404)

        cur.execute("""
            SELECT t.id, t.date, t.amount, c.name as category_name, t.description
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.owner_id = %s ORDER BY t.date DESC
        """, (user["id"],))
        rows = cur.fetchall()
        if not rows:
            raise AppException("No transactions found", 404)

        # CSV output
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Date", "Amount", "Category", "Description"])
        for row in rows:
            writer.writerow([row["id"], row["date"], row["amount"], row["category_name"], row["description"]])

        output.seek(0)
        filename = f"{username}_transactions.csv"

        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )


# ------------------------
# Get transactions with filters & pagination
# ------------------------
@router.get("/", response_model=list[schemas.TransactionOut])
def get_transactions(
    username: str = Depends(get_current_user),
    start: str | None = Query(None, description="Start date (YYYY-MM-DD)"),
    end: str | None = Query(None, description="End date (YYYY-MM-DD)"),
    category_id: int | None = Query(None, description="Filter by category ID"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    with get_cursor() as cur:
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        if not user:
            raise AppException("User not found", 404)

        query = """
            SELECT t.*, c.name as category_name
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.owner_id = %s
        """
        params = [user["id"]]

        if start:
            query += " AND t.date >= %s"
            params.append(start)
        if end:
            query += " AND t.date <= %s"
            params.append(end)
        if category_id:
            query += " AND t.category_id = %s"
            params.append(category_id)

        query += " ORDER BY t.date DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cur.execute(query, tuple(params))
        rows = cur.fetchall()
        return rows
