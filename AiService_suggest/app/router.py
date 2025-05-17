import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.chat_database import get_chat_db
from app.chat_model import ChatHistory
from app.schema import TripInput
from app.trip_recommender import generate_trip_plan
from app.user_database import get_user_db
from app.user_model import Member

router = APIRouter()

# 오늘 날짜 기준 파일명 생성
file_suffix = datetime.now().strftime("%Y%m%d")
filename = f"data/congestion_texts_{file_suffix}.json"

# 혼잡도 문장 로드
try:
    with open(filename, "r", encoding="utf-8") as f:
        congestion_texts = json.load(f)
except FileNotFoundError:
    congestion_texts = []

# 전체 문장을 문자열로 합치기
congestion_context = "\n".join(congestion_texts)

# POST 요청 처리 엔드포인트
@router.post("/suggest/{user_id}")
def recommend_trip(user_id: str, input_data: TripInput, db: Session = Depends(get_chat_db)):
    """
        사용자의 여행 정보를 바탕으로 여행 코스를 생성하고 DB에 저장한다.

        Args:
            user_id (str): 사용자 식별자 (경로 매개변수).
            input_data (TripInput): 사용자로부터 입력받은 여행 관련 정보.
            db (Session): 의존성 주입된 SQLAlchemy 세션 (채팅 기록용 DB).

        Returns:
            dict: 생성된 여행 일정 정보와 메타데이터를 포함하는 JSON 응답.

        Raises:
            HTTPException:
                - 400: 시작 시간이 종료 시간보다 이후일 경우
                - 500: 여행 경로 생성 또는 DB 저장 중 오류 발생 시

        Workflow:
            - 날짜 유효성 검증
            - LLM을 통한 여행 코스 생성
            - 생성된 결과를 chat_history 테이블에 저장
            - 사용자에게 응답 반환
        """
    # 날짜 논리 오류 확인
    if input_data.start_time >= input_data.finish_time:
        raise HTTPException(status_code=400, detail="Start time must be before finish time")

    # 여행 경로 생성
    try:
        result = generate_trip_plan(input_data, congestion_context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trip generation failed: {str(e)}")

    created_at = datetime.now()

    # DB 저장 시도
    record = ChatHistory(
        user_id=user_id,
        start_time=input_data.start_time,
        finish_time=input_data.finish_time,
        start_place=input_data.start_place,
        optional_request=input_data.optional_request,
        answer=result.content,
        created_at=created_at
    )

    try:
        db.add(record)
        db.commit()
        db.refresh(record)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return {
        "start_time": input_data.start_time,
        "finish_time": input_data.finish_time,
        "start_place": input_data.start_place,
        "optional_request": input_data.optional_request,
        "birth_year": input_data.birth_year,
        "gender": input_data.gender,
        "mbti": input_data.mbti,
        "answer": result.content,
        "created_at": created_at
    }

# GET 요청 처리 엔드포인트
@router.get("/suggest/{user_id}")
def get_user_history(user_id: str,
                     db1: Session = Depends(get_chat_db),
                     db2: Session = Depends(get_user_db)):
    """
    특정 사용자의 여행 추천 요청 기록 및 개인 정보를 조회한다.

    Args:
        user_id (str): 사용자 식별자 (경로 매개변수)
        db1 (Session): chat_history 테이블 접근을 위한 DB 세션
        db2 (Session): member 테이블 접근을 위한 DB 세션

    Returns:
        list[dict]: 사용자의 과거 여행 추천 기록 리스트
        - 각 항목에는 여행 시간, 요청사항, MBTI, 추천 결과 등이 포함됨

    Raises:
        HTTPException:
            - 404: 사용자 정보가 존재하지 않을 경우
            - 500: DB 조회 중 오류 발생 시
    """
    # DB 조회 로직
    try:
        # 채팅 기록 조회
        history = db1.query(ChatHistory) \
            .filter(ChatHistory.user_id == user_id) \
            .order_by(ChatHistory.created_at.desc()) \
            .all()

        # 사용자 정보 조회
        user = db2.query(Member).filter(Member.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    # 채팅 기록이 없는 경우
    if not history:
        return {"message": "No chat history found for this user."}

    return [
        {
            "start_time": h.start_time,
            "finish_time": h.finish_time,
            "start_place": h.start_place,
            "optional_request": h.optional_request,
            "birth_year": user.birth_year,
            "gender": user.gender,
            "mbti": user.mbti,
            "answer": h.answer,
            "created_at": h.created_at
        }
        for h in history
    ]