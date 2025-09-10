from fastapi import FastAPI
from app.routes import auth, transactions
from app.db import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Personal Finance Tracker")

app.include_router(auth.router)
app.include_router(transactions.router)

@app.get("/")
def root():
    return{"message": "Welcome to Personal Finance Tracker API"}