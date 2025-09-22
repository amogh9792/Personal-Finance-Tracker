from fastapi import FastAPI, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from app.utils.logger import logger
from app.core.exceptions import add_exception_handlers
from app.db_init import init_db
from app.routes import auth, transactions, admin
from app.core.config import settings
from app.routes import auth, transactions, categories


# Initialize DB tables
init_db()

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

app = FastAPI(
    title="Personal Finance Tracker",
    description="Finance tracker API with JWT, RBAC, and CRUD transactions",
    version="1.0.0"
)

# CORS (important for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Completed with status {response.status_code}")
    return response

# Add exception handlers
add_exception_handlers(app)

# Register routers
app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(admin.router)
app.include_router(categories.router)


@app.get("/")
def root():
    return {"message": "Welcome to Personal Finance Tracker API with RBAC"}
