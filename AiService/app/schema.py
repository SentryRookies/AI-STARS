# 요청 및 응답의 데이터 구조 정의

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
        from_attributes = True 
