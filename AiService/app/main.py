from fastapi import FastAPI
from .router import router
from .scheduler import start_scheduler

app = FastAPI()
start_scheduler()

app.include_router(router)
