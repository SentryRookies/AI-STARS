from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import database, crud, model, schema
from app.database import SessionLocal
from fastapi.responses import JSONResponse


router = APIRouter()

def get_db():
    """
       SQLAlchemy 세션을 생성하고 요청 종료 시 자동으로 닫는다.

       Returns:
        Generator[Session, None, None]: 데이터베이스 세션 객체
       """
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
    """
        리뷰 요약 데이터 생성

        Args:
            item : 생성할 요약 데이터 (ReviewSummarizeCreate)
            db (Session): DB 세션 (FastAPI Depends)

        Returns:
            ReviewSummarizeRead: 생성된 요약 데이터
        """
    print("🟡 요청 도착:", item.dict())
    db_item = model.ReviewSummarize(**item.dict())
    result = crud.create_summary(db, db_item)
    print("🟢 저장 완료:", result)
    return result

# type, id 기반 get 호출
@router.get("/summary/{target_type}/{target_id}")
def read_summary_by_target(target_type: str, target_id: str, db: Session = Depends(get_db)):
    """
        target_type 및 target_id 기준으로 요약 데이터 조회

        Args:
            target_type (str): 타겟 유형 (예: "accommodation", "cafe" 등)
            target_id (str): 타겟 고유 ID
            db (Session): DB 세션 (FastAPI Depends)

        Returns:
            ReviewSummarizeRead: 조회된 요약 데이터
    """
    result = crud.get_summary_by_target(db, target_id, target_type)
    if result:
        return {"target_id": target_id, "target_type": target_type, "content": result.content}
    return JSONResponse(status_code=404, content={"detail": "Summary not found"})