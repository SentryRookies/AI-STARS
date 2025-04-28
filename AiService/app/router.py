from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import database, crud, model, schema

router = APIRouter()

def getDb():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/summary/{targetId}", response_model=list[schema.ReviewSummarizeRead])
def readSummary(targetId: str, db: Session = Depends(getDb)):
    return crud.getSummaryByTargetId(db, targetId)

@router.post("/summary", response_model=schema.ReviewSummarizeRead)
def createSummary(item: schema.ReviewSummarizeCreate, db: Session = Depends(getDb)):
    print("🟡 요청 도착:", item.dict())
    dbItem = model.ReviewSummarize(**item.dict())
    result = crud.createSummary(db, dbItem)
    print("🟢 저장 완료:", result)
    return result
