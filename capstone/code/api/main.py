from fastapi import FastAPI
from app.database import init_db
from app.routers import turbine, management

app = FastAPI(
    title="Smart Turbine Health Analytics API",
)

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(turbine.router)
app.include_router(management.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message":"Turbine Health Analytics API"}