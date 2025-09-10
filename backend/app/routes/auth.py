from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
import psycopg2
from app.db import get_cursor
from app import schemas
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import settings
from app.utils.logger import logger
from app.core.exceptions import AppException

router = APIRouter(prefix="/auth", tags=["auth"])

# Register user
@router.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate):
    try:
        with get_cursor() as cur:
            cur.execute("SELECT id FROM users WHERE username = %s", (user.username,))
            existing = cur.fetchone()
            if existing:
                raise AppException("Username already exists", 400)

            hashed_pw = hash_password(user.password)
            cur.execute(
                "INSERT INTO users (username, hashed_password) VALUES (%s, %s) RETURNING id",
                (user.username, hashed_pw),
            )
            user_id = cur.fetchone()["id"]
            logger.info(f"New user registered: {user.username}")
            return {"id": user_id, "username": user.username}

    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        raise AppException("Could not register user", 500)

# Login user
@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        with get_cursor() as cur:
            cur.execute("SELECT * FROM users WHERE username = %s", (form_data.username,))
            user = cur.fetchone()
            if not user or not verify_password(form_data.password, user["hashed_password"]):
                raise AppException("Invalid username or password", 401)

            access_token = create_access_token({"sub": user["username"]})
            logger.info(f"User logged in: {user['username']}")
            return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise AppException("Could not login user", 500)
