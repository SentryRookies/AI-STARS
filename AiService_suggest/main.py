from fastapi import FastAPI
from app.createDB import create_tables
from app.es import save_congestion_to_json
from app.router import router

# FastAPI 인스턴스 생성
app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # 테이블 생성
    create_tables()
    # 혼잡도 문장 저장
    save_congestion_to_json()

app.include_router(router)