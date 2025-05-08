from fastapi import FastAPI
from app.router import router
from app.scheduler import start_scheduler
from app.createDB import create_tables

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    create_tables()
    start_scheduler()

app.include_router(router)
