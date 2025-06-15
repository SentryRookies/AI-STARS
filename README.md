# 🧑‍💻 AI-STARS - 장소 리뷰요약 & 개인 맞춤 여행 일정 추천

목표:서울시 관광지 혼잡도 관제 시스템에서 리뷰 요약과 여행지 추천 기능을 담당하는 AI 서비스 구성

---

## 🧩 프로젝트 구성

- **AiService**: 관광지, 숙소, 카페 등 장소별 사용자 리뷰 데이터를 분석하여 감정 분류 및 장단점 키워드를 추출하는 기능 제공
- **AiService_suggest**: 사용자 정보(MBTI, 나이, 성별, 일정 등)를 기반으로 혼잡도 정보를 결합하여 LLM 기반 관광지 추천 제공
- **.github**: EKS 배포

---

## 📌 프로젝트 개요

- 키워드 기반 요약을 통해 복잡한 리뷰를 빠르게 파악 가능
- 시간대별 혼잡도 반영하여 실시간 맞춤 여행지 추천

---
### ✔️ AiService: 리뷰 요약

- **기능**: 
  - KoBERT 기반 감정 분석 모델 학습 및 적용
  - SBERT 기반 유사도 분석을 통한 키워드 추출
  - 긍/부정 키워드 통계 및 긍/부정 각각 상위 5개의 요약된 키워드 제공
- **요약 절**:
  - 리뷰 수집 → 문장 분리 → 감정 분류 → 키워드 추출 → 요약 생성
- **반환 예시**:
  ```json
  {
    "positiveKeywords": ["전망/경치", "전반적", "분위기", "음식", "시설"],
    "negativeKeywords": ["혼잡", "주차", "선택지/메뉴", "위생"],
    "positiveCount": 96
    "negativeCount": 55
  }
  ```
- **API URL**: `POST /place/summary/[targetType]/{placecode}`

---

### ✔️ AiService_suggest: 개인 맞춤 추천

- **기능**:
  - MBTI/나이/성별 기본 정보 및 여행 일정과 요구사항에 맞춰 여행 일정 추천 기능 제공
  - LangChain + OpenAI 프롬프트 구성
  - Elasticsearch RAG (혼잡도 정보)
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
    "answer":"28세 여성 INTP의 분석적이고 호기심 많은 성향을 고려해 여유로운 탐구와 깔끔한 동선으로 구성한 서울 예행 일정입니다.\n\n⏰ 일정표 (5/14 13:00 출발 ~ 5/15 18:00 도착)\n\n▶ 5월 14일 (수요일)\n🕐 13:00 – 인천공항 출발\n- 🚆 공항철도 A’REX 직통 (소요 68분, 약 9,500원)\n...중략...\n📌 Tip: INTP 성향에 맞춰 전시와 산책 위주로 여유 있게 배치했으며, 카페 브레이크로 리듬을 조절하세요.",
    "created_at":"2025-05-13T13:01:24"
    
  }
  ```
- **API URL**: `POST /user/suggest/{user_id}`

---

##⚙️ 기술 스택

| 범주 | 기술 |
|--|--|
| 서버 구성 | FastAPI, PostgreSQL |
| AI 모델 | KoBERT, SBERT, PyTorch, LangChain, OpenAI |
| 데이터 | Elasticsearch, Playwright, Kafka |
| 호출 | FastAPI, Postman |
| 환경 | Docker, Kubernetes, AWS, Terraform, GitHub |

---


## 발표 예시 이미지

> 리뷰 요약 결과  
![summary-demo](images/summary_result.png)

> 개인 추천 결과  
![recommend-demo](images/recommend_result.png)

---

## 💁‍♂️ AI 팀원
|AI 팀장|AI 팀원|
|:---:|:---:|
|김지수|안재훈|
