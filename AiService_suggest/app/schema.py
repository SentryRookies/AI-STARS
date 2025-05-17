from pydantic import BaseModel
from datetime import datetime

class TripInput(BaseModel):
    birth_year: int
    gender: str
    mbti: str
    start_time: datetime
    finish_time: datetime
    question_type: int
    start_place: str
    optional_request: str