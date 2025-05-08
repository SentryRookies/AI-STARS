from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import database, crud, model, schema
from app.database import SessionLocal
from fastapi.responses import JSONResponse


router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
# id 기반 get 호출
# @router.get("/summary/{target_id}", response_model=list[schema.ReviewSummarizeRead])
# def read_summary(target_id: str, db: Session = Depends(get_db)):
#     return crud.get_summary_by_target_id(db, target_id)

@router.post("/summary", response_model=schema.ReviewSummarizeRead)
def create_summary(item: schema.ReviewSummarizeCreate, db: Session = Depends(get_db)):
    print("🟡 요청 도착:", item.dict())
    db_item = model.ReviewSummarize(**item.dict())
    result = crud.create_summary(db, db_item)
    print("🟢 저장 완료:", result)
    return result

# type, id 기반 get 호출
@router.get("/summary/{target_type}/{target_id}")
def read_summary_by_target(target_type: str, target_id: str, db: Session = Depends(get_db)):
    result = crud.get_summary_by_target(db, target_id, target_type)
    if result:
        return {"target_id": target_id, "target_type": target_type, "content": result.content}
    return JSONResponse(status_code=404, content={"detail": "Summary not found"})