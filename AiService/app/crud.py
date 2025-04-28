# DB CRUD
from sqlalchemy.orm import Session
from . import model

# 저장 (create)
def create_summary(db: Session, summary_data: model.ReviewSummarize):
    try:
        print("🔵 DB 추가 시도")
        db.add(summary_data)
        db.commit()
        db.refresh(summary_data)
        print("🟢 DB 커밋 완료")
        return summary_data
    except Exception as e:
        print("❌ 예외 발생:", e)
        db.rollback()
        raise


# 조회 (read)
def get_summary_by_target_id(db: Session, target_id: str):
    return db.query(model.ReviewSummarize).filter(model.ReviewSummarize.target_id == target_id).all()
