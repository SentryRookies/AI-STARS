from pydantic import BaseModel
from datetime import datetime

class TripInput(BaseModel):
    """여행지 추천에 사용할 사용자 정보"""
    birth_year: int
    gender: str
    mbti: str
    start_time: datetime
    finish_time: datetime
    question_type: int
    start_place: str
    optional_request: str