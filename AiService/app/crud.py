# app/crud.py

from sqlalchemy.orm import Session
from . import model

# 저장 (create)
def create_summary(db: Session, summary_data: model.Review_summarize):
    """
        새로운 리뷰 요약을 데이터베이스에 저장한다.

        Args:
            db (Session): SQLAlchemy 세션
            summary_data (ReviewSummarize): 저장할 요약 데이터 모델 객체

        Returns:
            ReviewSummarize: 저장된 데이터
    """
    try:
        print(" DB 추가 시도")
        db.add(summary_data)
        db.commit()
        db.refresh(summary_data)
        print(" DB 커밋 완료")
        return summary_data
    except Exception as e:
        print(" 예외 발생:", e)
        db.rollback()
        raise

# 조회 (read)
def get_summary_by_target_id(db: Session, target_id: str):
    """
    target_id 기준으로 요약 데이터를 모두 조회한다.

    Args:
        db (Session): SQLAlchemy 세션
        target_id (str): 조회할 타겟 ID

    Returns:
        list[ReviewSummarize]: 해당 타겟의 모든 요약 데이터
    """
    return db.query(model.Review_summarize).filter(model.Review_summarize.target_id == target_id).all()

def get_summary_by_target(db: Session, target_id: str, target_type: str):
    """
    target_id와 target_type 기준으로 최신 요약 데이터를 조회한다.

    Args:
        db (Session): SQLAlchemy 세션
        target_id (str): 타겟 ID
        target_type (str): 타겟 유형

    Returns:
        ReviewSummarize | None: 가장 최근의 요약 데이터 (없으면 None)
    """
    return (
        db.query(model.Review_summarize)
        .filter(model.Review_summarize.target_id == target_id)
        .filter(model.Review_summarize.target_type == target_type)
        .order_by(model.Review_summarize.review_id.desc())  # 최신순 정렬 (선택)
        .first()
    )
