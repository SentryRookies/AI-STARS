# app/schema.py

from pydantic import BaseModel

# POST용 (요청용)
class ReviewSummarizeCreate(BaseModel):
    target_id: str
    target_type: str
    content: str

# GET용 (응답용)
class ReviewSummarizeRead(ReviewSummarizeCreate):
    id: int

    class Config:
        from_attributes = True  # ✅ pydantic v2용 옵션 (ORM 연동)
