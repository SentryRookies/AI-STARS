
# 🧭 AiService_suggest - 개인 맞춤 관광지 추천

LangChain 기반 LLM 프롬프트를 활용하여  
사용자 성향 및 실시간 혼잡도 정보를 바탕으로 관광지를 추천하는 FastAPI 서버입니다.

---

## ✅ 주요 기능

- 성별, 나이, MBTI, 일정 등 사용자 정보 기반 추천
- 실시간 혼잡도 정보 필터링 (Elasticsearch) 검색 기반 정적 RAG 구조 사용
- LangChain + OpenAI 기반 프롬프트 구성

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

