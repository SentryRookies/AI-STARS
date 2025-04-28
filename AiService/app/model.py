# SQLAlchemy 모델 정의
from sqlalchemy import Column, Integer, String, Text
from .database import Base  # database.py에서 Base 가져오기

class ReviewSummarize(Base):
    __tablename__ = "review_summarize"

    review_id = Column(Integer, primary_key=True, index=True)
    target_id = Column(String(20), nullable=False)
    target_type = Column(String(20), nullable=False)
    sentiment = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
