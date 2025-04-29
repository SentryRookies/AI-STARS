# app/model.py

from sqlalchemy import Column, Integer, String, Text
from .database import Base

class Review_summarize(Base):
    __tablename__ = "review_summarize"

    review_id = Column(Integer, primary_key=True, index=True)
    target_id = Column(String(20), nullable=False)
    target_type = Column(String(20), nullable=False)
    sentiment = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
