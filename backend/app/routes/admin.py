from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from app.db import get_cursor
from app.core.security import decode_access_token
from app.core.exceptions import AppException

router = APIRouter(prefix="/admin", tags=["admin"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    """Extract username from JWT token"""
    payload = decode_access_token(token)
    if not payload:
        raise AppException("Invalid or expired token", 401)
    return payload["sub"]

def require_admin(username: str):
    """Check if user is admin"""
    with get_cursor() as cur:
        cur.execute("SELECT is_admin FROM users WHERE username = %s", (username,))
        row = cur.fetchone()
        if not row or not row["is_admin"]:
            raise AppException("Forbidden: Admins only", 403)
    return True


@router.get("/users")
def list_users(username: str = Depends(get_current_user)):
    """List all users (Admin only)"""
    require_admin(username)
    with get_cursor() as cur:
        cur.execute("SELECT id, username, is_admin FROM users ORDER BY id")
        return cur.fetchall()


@router.patch("/make-admin/{user_id}")
def make_admin(user_id: int, username: str = Depends(get_current_user)):
    """Promote a user to admin"""
    require_admin(username)
    with get_cursor() as cur:
        cur.execute("UPDATE users SET is_admin = TRUE WHERE id = %s RETURNING id, username, is_admin", (user_id,))
        updated = cur.fetchone()
        if not updated:
            raise AppException("User not found", 404)
        return updated


@router.patch("/remove-admin/{user_id}")
def remove_admin(user_id: int, username: str = Depends(get_current_user)):
    """Demote a user (remove admin rights)"""
    require_admin(username)
    with get_cursor() as cur:
        cur.execute("UPDATE users SET is_admin = FALSE WHERE id = %s RETURNING id, username, is_admin", (user_id,))
        updated = cur.fetchone()
        if not updated:
            raise AppException("User not found", 404)
        return updated
