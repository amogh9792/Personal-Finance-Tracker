from fastapi import APIRouter, Depends, Path
from fastapi.security import OAuth2PasswordBearer
from app.db import get_cursor
from app import schemas
from app.core.security import decode_access_token
from app.core.exceptions import AppException
from app.utils.logger import logger

router = APIRouter(prefix="/categories", tags=["categories"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise AppException("Invalid or expired token", 401)
    return payload["sub"]


# ------------------------
# Create category
# ------------------------
@router.post("/", response_model=schemas.CategoryOut)
def create_category(cat: schemas.CategoryCreate, username: str = Depends(get_current_user)):
    with get_cursor() as cur:
        # find user
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        if not user:
            raise AppException("User not found", 404)

        cur.execute(
            "INSERT INTO categories (name, user_id) VALUES (%s, %s) RETURNING id, name, user_id",
            (cat.name.capitalize(), user["id"]),
        )
        new_cat = cur.fetchone()
        logger.info(f"✅ Category created by {username}: {cat.name}")
        return new_cat


# ------------------------
# List categories
# ------------------------
@router.get("/", response_model=list[schemas.CategoryOut])
def list_categories(username: str = Depends(get_current_user)):
    with get_cursor() as cur:
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        if not user:
            raise AppException("User not found", 404)

        cur.execute("SELECT id, name, user_id FROM categories WHERE user_id = %s", (user["id"],))
        rows = cur.fetchall()
        return rows


# ------------------------
# Delete category
# ------------------------
@router.delete("/{cat_id}")
def delete_category(cat_id: int = Path(...), username: str = Depends(get_current_user)):
    with get_cursor() as cur:
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        if not user:
            raise AppException("User not found", 404)

        cur.execute("DELETE FROM categories WHERE id = %s AND user_id = %s RETURNING id", (cat_id, user["id"]))
        deleted = cur.fetchone()
        if not deleted:
            raise AppException("Category not found or not owned by user", 404)

        logger.info(f"🗑️ Category {cat_id} deleted by {username}")
        return {"message": f"Category {cat_id} deleted successfully"}
