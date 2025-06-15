# 🧑‍💻 AI-STARS - 장소 리뷰 요약 & 개인 맞춤 여행 일정 추천

**목표:** 서울시 관광지 혼잡도 관제 시스템에서 리뷰 요약과 여행지 추천 기능을 담당하는 AI 서비스 구성

---

## 🧩 프로젝트 구성

- **AiService**: 장소별 사용자 리뷰 데이터를 분석하여 감정 분류 및 장단점 키워드 추출
- **AiService_suggest**: 사용자 정보(MBTI, 나이, 성별, 일정 등) + 혼잡도 정보를 기반으로 LLM 기반 관광지 추천
- **.github**: EKS 기반 자동 배포 환경 구성

---

## 📌 프로젝트 개요

- 복잡한 리뷰를 **키워드 기반으로 요약**해 빠르게 파악 가능
- **시간대별 혼잡도 + 사용자 성향**을 반영한 맞춤형 여행지 추천 제공

---

## ✔️ AiService: 리뷰 요약

- **주요 기능**:
  - KoBERT 기반 감정 분석 모델 학습 및 적용
  - SBERT 기반 유사도 분석으로 키워드 추출
  - 긍/부정 키워드 각각 상위 5개 요약 제공

- **요약 절차**:
  리뷰 수집 → 문장 분리 → 감정 분류 → 키워드 추출 → 요약 생성

- **API URL**: `GET /place/summary/[targetType]/{placecode}`

- **반환 예시**:
  ```json
  {
    "positiveKeywords": ["전망/경치", "전반적", "분위기", "음식", "시설"],
    "negativeKeywords": ["혼잡", "주차", "선택지/메뉴", "위생"],
    "positiveCount": 96,
    "negativeCount": 55
  }
  ```

---

## ✔️ AiService_suggest: 개인 맞춤 추천

- **주요 기능**:
  - MBTI/나이/성별/일정 기반 맞춤 여행 코스 추천
  - LangChain + OpenAI를 통한 프롬프트 구성 및 응답 생성
  - Elasticsearch를 활용해 실시간 혼잡도 정보 반영 (RAG 구조 적용)

- **API URL**: `GET /user/suggest/{user_id}`

- **반환 예시**:
  ```json
  {
    "start_time": "2025-05-14T13:00:00",
    "finish_time": "2025-05-15T18:00:00",
    "start_place": "인천공항",
    "optional_request": "2",
    "birth_year": 1998,
    "gender": "F",
    "mbti": "INTP",
    "answer": "28세 여성 INTP의 분석적이고 호기심 많은 성향을 고려해 여유로운 탐구와 깔끔한 동선으로 구성한 서울 예행 일정입니다.\n\n⏰ 일정표 (5/14 13:00 출발 ~ 5/15 18:00 도착)\n...중략...\n📌 Tip: INTP 성향에 맞춰 전시와 산책 위주로 여유 있게 배치했으며, 카페 브레이크로 리듬을 조절하세요.",
    "created_at": "2025-05-13T13:01:24"
  }
  ```

---

## ⚙️ 기술 스택

| 범주 | 기술 |
|------|------|
| 서버 구성 | FastAPI, PostgreSQL |
| AI 모델 | KoBERT, SBERT, PyTorch, LangChain, OpenAI |
| 데이터 처리 | Elasticsearch, Kafka, Playwright |
| API 테스트 | Postman |
| 인프라 환경 | Docker, Kubernetes, AWS, Terraform, GitHub |

---

## 🖼️ 시연 이미지

> **리뷰 요약 결과**  
![[summary-demo](images/summary_result.png)](https://private-user-images.githubusercontent.com/127455884/455257928-1cdad800-3d31-4687-a152-b065faf4a72c.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NDk5OTI1NDEsIm5iZiI6MTc0OTk5MjI0MSwicGF0aCI6Ii8xMjc0NTU4ODQvNDU1MjU3OTI4LTFjZGFkODAwLTNkMzEtNDY4Ny1hMTUyLWIwNjVmYWY0YTcyYy5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNjE1JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDYxNVQxMjU3MjFaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT0xNGU1NTQwNzY5YjJlNGY0YTc2ZmJiMmE3NzNiMzA0ZTk2NjI2ZWRhNDc2OTFhMzdjNjM5OTE3Y2M0NGVlZGVjJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.0CRpL4sDM0gf2VnpjgTphSTWThFAtTj8UrGNv6EngcY)

> **개인 맞춤 추천 결과**  
![recommend-demo](images/recommend_result.png)

---

## 🙋‍♂️ AI 팀원 소개

| AI 팀장 | AI 팀원 |
|:--------:|:--------:|
| 김지수 | 안재훈 |
