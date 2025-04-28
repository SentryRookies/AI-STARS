# Pydantic 요청/응답 모델
from pydantic import BaseModel

# POST용 (요청용)
class ReviewSummarizeCreate(BaseModel):
    target_id: str
    target_type: str
    sentiment: str
    content: str

# GET용 (응답용)
class ReviewSummarizeRead(ReviewSummarizeCreate):
    id: int

    class Config:
        from_attributes = True  # ✅ pydantic v2 버전용 옵션
