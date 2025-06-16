
# 🧭 AiService_suggest - 개인 맞춤 관광지 추천

LangChain 기반 LLM 프롬프트를 활용하여  
사용자 성향 및 실시간 혼잡도 정보를 바탕으로 관광지를 추천하는 FastAPI 서버입니다.

---

## ✅ 주요 기능

- 성별, 나이, MBTI, 일정 등 사용자 정보 기반 추천
- 실시간 혼잡도 정보 필터링 (Elasticsearch) 검색 기반 정적 RAG 구조 사용
- LangChain + OpenAI 기반 프롬프트 구성

(https://private-user-images.githubusercontent.com/127455884/455336723-e779109e-c665-497c-9254-40477f63ceee.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTAwNDg1ODksIm5iZiI6MTc1MDA0ODI4OSwicGF0aCI6Ii8xMjc0NTU4ODQvNDU1MzM2NzIzLWU3NzkxMDllLWM2NjUtNDk3Yy05MjU0LTQwNDc3ZjYzY2VlZS5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNjE2JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDYxNlQwNDMxMjlaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT0zMTY4OWU5MjU0YTNjMTY0MDM0MGUzY2YwY2U3YWYzMjcwMGM1MGI2MjE4ZTg4Y2M5MjhiMmU2YWU4YTUxZGJjJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.rMRNG6ZAhz05kw2TPECrSft7LB62qUwWAN5Zqev2MX4)

---

## ▶️ 실행 방법

1. 의존성 설치
```bash
pip install -r requirements.txt
```

2. 서버 실행
```bash
uvicorn app.main:app --reload
```

---

## 🔁 처리 과정

1. 사용자 입력값 수신 (일정, MBTI, 출발지 등)
2. 프롬프트 자동 생성
3. RAG 기반 검색 (Elasticsearch + FAISS)
4. LLM 응답 생성 및 추천 결과 반환

---

## 📁 프로젝트 디렉토리 구조 (AiService_suggest)

```bash
AiService_suggest/
├── app/                         # 추천 기능을 위한 FastAPI 서버 구성
│   ├── chat_database.py        # 채팅 관련 DB 연결 설정
│   ├── chat_model.py           # 채팅 기록 데이터 모델
│   ├── createDB.py             # DB 초기 스키마 생성 스크립트
│   ├── es.py                   # Elasticsearch 연동 및 쿼리 처리 모듈
│   ├── router.py               # FastAPI 라우팅 설정
│   ├── schema.py               # 요청 및 응답을 위한 Pydantic 스키마 정의
│   ├── trip_recommender.py     # 여행지 추천 로직 구현
│   ├── user_database.py        # 사용자 관련 DB 설정
│   └── user_model.py           # 사용자 정보 데이터 모델
│
├── main.py                    # FastAPI 앱 실행 진입점
├── Dockerfile                 # Docker 빌드 설정
├── .dockerignore              # Docker 제외 파일 설정
├── .gitignore                 # Git 제외 파일 설정
├── requirements.txt           # 의존 패키지 리스트
```

---
