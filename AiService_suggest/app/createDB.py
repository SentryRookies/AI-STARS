from app.chat_database import chat_engine
from app.chat_model import Base

def create_tables():
    Base.metadata.create_all(bind=chat_engine)