# app/schema.py

from pydantic import BaseModel

# POST용 (요청용)
class ReviewSummarizeCreate(BaseModel):
    """
    리뷰 요약 생성 요청 모델

    Attributes:
        target_id (str): 요약 대상의 고유 ID
        target_type (str): 요약 대상의 유형 (예: accommodation, place 등)
        content (str): 요약된 리뷰 내용
    """

    target_id: str
    target_type: str
    content: str

# GET용 (응답용)
class ReviewSummarizeRead(ReviewSummarizeCreate):
    """
       리뷰 요약 응답 모델 (읽기 전용)

       Attributes:
           id (int): 데이터베이스에 저장된 요약 데이터의 고유 ID
           target_id (str): 요약 대상의 고유 ID
           target_type (str): 요약 대상의 유형
           content (str): 요약된 리뷰 내용
    """
    id: int

    class Config:
        from_attributes = True  #  pydantic v2용 옵션 (ORM 연동)
