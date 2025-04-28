from fastapi import FastAPI
from app.router import router
from app.scheduler import startScheduler

app = FastAPI()

@app.on_event("startup")
async def startupEvent():
    startScheduler()

app.include_router(router)
