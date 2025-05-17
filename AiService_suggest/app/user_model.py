from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Member(Base):
    __tablename__ = "member"

    user_id = Column(String(100), primary_key=True, autoincrement=True)
    birth_year = Column(Integer, nullable=False)
    gender = Column(String(100), nullable=False)
    mbti = Column(String(100), nullable=False)