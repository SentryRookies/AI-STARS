# app/create_tables.py

from .database import engine
from .model import Base

def create_tables():
    """데이터베이스에 생성된 모든 테이블 생성"""
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
