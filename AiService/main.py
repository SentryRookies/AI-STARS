from fastapi import FastAPI
from app.router import router
from app.scheduler import start_scheduler
from app.createDB import create_tables

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # DB 테이블 생성
    create_tables()
    # 배치 스케줄러 실행
    start_scheduler()

app.include_router(router)
