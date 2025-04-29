from fastapi import FastAPI
from app.router import router
from app.scheduler import start_scheduler

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    start_scheduler()

app.include_router(router)
