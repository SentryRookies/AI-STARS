# 📝 AiService - 장소 리뷰 요약 서비스

FastAPI 기반 장소 키워드 리뷰 요약 AI 서버입니다.  
KoBERT 기반 감정 분석과 SBERT 기반 유사도 분석을 통해 긍/부정 키워드 및 요약문을 제공합니다.

---

## ✅ 주요 기능

- 장소 리뷰 문장을 감정(긍정/부정/중립)으로 분류
- 긍정/부정 키워드 상위 5개 추출
- 리뷰 내용을 요약한 자연어 문장 생성

---

## 🔁 처리 과정

1. 리뷰 수집 (카페, 숙소, 관광지, 음식점 등) 
2. 문장 분리 및 정제
3. 감정 분석 (KoBERT fine-tuning)
4. 키워드 추출 (SBERT 유사도 기반)
5. 통계 및 요약문 생성

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

## 📁 프로젝트 디렉토리 구조 (AiService)

```bash
AiService/
├── app/                         # FastAPI 서버 및 DB 연동 로직
│   ├── migrations/              # Alembic DB 마이그레이션
│   │   └── createDB.py         # 초기 DB 스키마 생성 스크립트
│   ├── crud.py                 # DB CRUD 함수 정의
│   ├── database.py             # DB 연결 설정
│   ├── model.py                # SQLAlchemy 모델 정의
│   ├── router.py               # FastAPI 라우팅 설정
│   ├── schema.py               # 요청/응답 스키마 정의
│   └── scheduler.py            # APScheduler를 활용한 주기적 작업 예약 스크립트
│
├── batch/                      # 배치 처리 및 모델 연동 로직
│   ├── keyword_mapping/        # 키워드 사전 매핑 파일
│   │   ├── negative_keyword_mapping.json  # 부정 키워드 매핑
│   │   └── positive_keyword_mapping.json  # 긍정 키워드 매핑
│   ├── emotion_model.py        # 감정 분석 모델 로직
│   └── keyword_model.py        # 키워드 추출 로직
│
├── crawler/                    # 리뷰 크롤링 스크립트
│   └── crawling.py             # DB에 등록된 장소의 카카오맵 리뷰 크롤링
│
├── data/                       # 리뷰 데이터 저장 디렉토리
│
├── finetunning/               # 감정 분석 모델 파인튜닝
│   └── finetunning.ipynb      # 파인튜닝에 사용한 코드
│
├── main.py                    # FastAPI 앱 실행 진입점
├── Dockerfile                 # Docker 빌드 설정
├── .dockerignore              # Docker 제외 파일 설정
├── .gitignore                 # Git 제외 파일 설정
├── README.md
└── requirements.txt           # 의존 라이브러리 목록
```
---

## 📦 모델 선정

1. [감정 분석 모델(KoBERT)](https://huggingface.co/alsgyu/sentiment-analysis-fine-tuned-model)

   7600개의 장소 리뷰 데이터를 사용하여 지도 학습 후 모델 사용
   | Parameter       | 기본 설정 | 1차   | 2차     | 3차     | 4차     | 5차   | 6차   | n차   | 최종 설정 |
  |----------------|-----------|--------|----------|----------|----------|--------|--------|--------|-------------|
  | **Learning rate**     | 2e-5      | 2e-5   | **2e-6** | **5e-6** | **1e-5** | 2e-5   | **3e-5** | **1e-5** | 2e-5 |
  | **Train batch size**  | 8         | 8      | 8        | 8        | **16**   | 8      | **16**  | **16**  | 16 |
  | **Eval batch size**   | 8         | 8      | 8        | 8        | 8        | 8      | **32**  | **32**  | 32 |
  | **Epochs**            | 3         | **5**  | **5**    | **10**   | **10**   | **5**  | **7**   | **12**  | 10 |
  | **Weight decay**      | 0.01      | 0.01   | 0.01     | **0.05** | **0.02** | 0.01   | **0.05**| **0.03**| 0.05 |
  | **LR scheduler**      | 없음      | 없음   | 없음     | 없음     | **Cosine** | 없음 | **Cosine** | **Cosine** | Cosine |
  | **Warmup ratio**      | 없음      | 없음   | 없음     | 없음     | 없음     | 없음 | **0.1**  | **0.1**  | 0.1 |
   
3. [키워드 추출 모델(SBERT)](https://huggingface.co/jhgan/ko-sbert-nli)

   
## 🔧 감정 분석 모델 하이퍼파라미터 튜닝 과정

| Parameter       | 기본 설정 | 1차   | 2차     | 3차     | 4차     | 5차   | 6차   | n차   | 최종 설정 |
|----------------|-----------|--------|----------|----------|----------|--------|--------|--------|-------------|
| **Learning rate**     | 2e-5      | 2e-5   | **2e-6** | **5e-6** | **1e-5** | 2e-5   | **3e-5** | **1e-5** | 2e-5 |
| **Train batch size**  | 8         | 8      | 8        | 8        | **16**   | 8      | **16**  | **16**  | 16 |
| **Eval batch size**   | 8         | 8      | 8        | 8        | 8        | 8      | **32**  | **32**  | 32 |
| **Epochs**            | 3         | **5**  | **5**    | **10**   | **10**   | **5**  | **7**   | **12**  | 10 |
| **Weight decay**      | 0.01      | 0.01   | 0.01     | **0.05** | **0.02** | 0.01   | **0.05**| **0.03**| 0.05 |
| **LR scheduler**      | 없음      | 없음   | 없음     | 없음     | **Cosine** | 없음 | **Cosine** | **Cosine** | Cosine |
| **Warmup ratio**      | 없음      | 없음   | 없음     | 없음     | 없음     | 없음 | **0.1**  | **0.1**  | 0.1 |



---
