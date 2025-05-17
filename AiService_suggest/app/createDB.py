from app.chat_database import chat_engine
from app.chat_model import Base

def create_tables():
    "채팅기록 테이블 없을 경우 생성"
    Base.metadata.create_all(bind=chat_engine)