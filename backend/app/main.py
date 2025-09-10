from fastapi import FastAPI, Request
from fastapi.security import OAuth2PasswordBearer
from app.utils.logger import logger
from app.core.exceptions import add_exception_handlers
from app.db_init import init_db
from app.routes import auth, transactions

# Auto-create tables
init_db()

# Define OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

app = FastAPI(
    title="Personal Finance Tracker",
    description="A personal finance tracker API with JWT authentication",
    version="1.0.0"
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Completed with status {response.status_code}")
    return response

# Custom exception handlers
add_exception_handlers(app)

# Routers
app.include_router(auth.router)
app.include_router(transactions.router)

@app.get("/")
def root():
    return {"message": "Welcome to Personal Finance Tracker API (with JWT)"}
