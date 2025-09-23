# app/main.py

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers import management, turbine

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Database has been initialized.")
    yield
    print("Application is shutting down.")

app = FastAPI(
    title="Turbine Monitoring API",
    description="API for monitoring and managing gas turbine data.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(turbine.router, prefix="/data", tags=["Data & Analytics"])
app.include_router(management.router, prefix="/turbines", tags=["Management"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Turbine Monitoring API"}