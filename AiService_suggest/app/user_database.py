# app/chat_database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# .env 로드
load_dotenv()

# DB 연결 URL 구성
USER_DB_URL = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('USER_DB_NAME')}"
)

# 엔진 및 세션 구성
user_engine = create_engine(USER_DB_URL)
UserSessionLocal = sessionmaker(bind=user_engine, autocommit=False, autoflush=False)  # 대문자 L

# DB 세션 주입 함수
def get_user_db():
    db = UserSessionLocal()
    try:
        yield db
    finally:
        db.close()