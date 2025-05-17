from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ChatHistory(Base):
    __tablename__ = "chat_history"

    chat_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False)
    start_time = Column(TIMESTAMP, nullable=False)
    finish_time = Column(TIMESTAMP, nullable=False)
    start_place = Column(String(100), nullable=False)
    optional_request = Column(Text)
    answer = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)