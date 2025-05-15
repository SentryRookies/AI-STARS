# app/model.py

from sqlalchemy import Column, Integer, String, Text
from .database import Base

class Review_summarize(Base):
    """ 리뷰 요약 정보를 저장하는 SqlAlchemy 모델"""
    __tablename__ = "review_summarize"

    review_id = Column(Integer, primary_key=True, index=True)
    target_id = Column(String(20), nullable=False)
    target_type = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
