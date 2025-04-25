# app/router.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from . import database, crud, model, schema

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/summary/{target_id}")
def read_summary(target_id: str, db: Session = Depends(get_db)):
    return crud.get_summary_by_target_id(db, target_id)

@router.post("/summary")
def create_summary(item: schema.ReviewSummarizeCreate, db: Session = Depends(get_db)):
    print("🟡 요청 도착:", item.dict())
    db_item = model.ReviewSummarize(**item.dict())
    result = crud.create_summary(db, db_item)
    print("🟢 저장 완료:", result)
    return result