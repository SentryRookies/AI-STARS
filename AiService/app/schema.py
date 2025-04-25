# app/schema.py
from pydantic import BaseModel

class ReviewSummarizeCreate(BaseModel):
    target_id: str
    target_type: str
    sentiment: str
    content: str

    class Config:
        orm_mode = True
