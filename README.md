# 🧑‍📛 AI Service - 관광지 리뷰요약 & 연합 일정 추천

목표: 관광지 정보와 사용자 성향을 고려한 AI 기능을 통해 전달과 리뷰를 효율적으로 제공하는 서비스입니다.

---

## 프로젝트 구성

- **AiService**: 포스트 기본 의견 리뷰를 검정 및 후기와 같은 것을 구문 다운 중 것을 판단하고, 키워드로 통계 하는 기능
- **AiService_suggest**: 사용자 성향 (MBTI, 나이, 성목) 기본으로 가장 적절한 관광지를 RAG 구조를 통해 추천

---

## 프로젝트 개요

- 가장 필요한 것만 검색하고, 더 가까운 추천을 받는 관광 서비스
- 시간이 줄어진 리뷰 검색
- 시간변동에 맞게 원하는 장소 방문 가능

---
### ✔️ AiService: 리뷰 요약

- **기능**: KoBERT 가설 검정 및 키워드 추출
- **시작 방식**:
  - 문장 분리 → 검정 분류 → 기술 추출
- **반환 예시**:
  ```json
  {
    "positive_keywords": ["천정함", "뷰가 좋음"],
    "negative_keywords": ["혼작함"],
    "summary": "천정한 서비스와 좋은 뷰가 인상적이잖아, 혼작한 점이 아쉬운 목적"
  }
  ```
- **API URL**: `POST /review/summarize`

---

### ✔️ AiService_suggest: 개인 맞춤 추천

- **기능**:
  - MBTI/나이/성목 기본 정보 및 시간변동 현재 호화도와 연계
  - Elasticsearch RAG (무효 장소 제외 지정)
  - LangChain + OpenAI 프롬프트 구성
- **반환 예시**:
  ```json
  {
    "recommended_places": ["서울수르", "한강공원"],
    "why": "ENFP 성향과 시간변동 호화도 기준에 적합한 장소입니다."
  }
  ```
- **API URL**: `POST /recommend`

---

## 필수 기술

| 보존 | 기술 |
|--|--|
| 프론트엔드 | React, TypeScript, Vite, TailwindCSS |
| 백엔드 | Spring Boot, PostgreSQL, Redis, FastAPI |
| AI 모델 | KoBERT, SBERT, PyTorch, LangChain, OpenAI |
| 데이터 | Elasticsearch, Playwright, Kafka |
| 호출 | FastAPI, Postman |
| 환경 | Docker, Kubernetes, AWS, Terraform, GitHub |

---

## 발사 방식

```bash
# 리뷰 요약
cd AiService
uvicorn app.main:app --reload

# 개인 추천
cd AiService_suggest
uvicorn app.main:app --reload
```

---

## ㅋ 발표 예시 이미지

> 리뷰 요약 결과  
![summary-demo](images/summary_result.png)

> 개인 추천 결과  
![recommend-demo](images/recommend_result.png)

---

## 답변 관련 책임 기능

- 검정분석 모델 파인튜닝 & API 구현
- LangChain 프롬프트 구성 및 LLM 연동
- Elasticsearch 구조 및 시간변동 호화도 조회
