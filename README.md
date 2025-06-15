# 🧑‍💻 AI Service - 장소 리뷰요약 & 개인 맞춤 여행 일정 추천

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
    "recommended_places": ["서울수르", "한강공원"],
    "why": "ENFP 성향과 시간변동 호화도 기준에 적합한 장소입니다."
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
