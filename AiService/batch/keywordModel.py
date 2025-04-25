from app.database import SessionLocal
from app.model import ReviewSummarize

from batch.crawler.naver_review import crawl_reviews
from batch.analyzer.sentiment_batch import analyze_reviews
from batch.keyword.keyword_extractor import extract_top_keywords

import asyncio

def crawl_and_analyze():
    print("📦 [스케줄러] 리뷰 수집 및 분석 시작")

    db = SessionLocal()

    try:
        # 1. 크롤링 (비동기 → 동기로 실행)
        reviews = asyncio.run(crawl_reviews())

        # 2. 감정 분석
        analyzed_data = analyze_reviews(reviews)  # List[dict] ← text, label, score

        # 3. 키워드 추출 (단순 출력, DB에는 저장하지 않음)
        extract_top_keywords(analyzed_data)

        # 4. DB 저장
        for item in analyzed_data:
            label = item["label"]
            content = item["text"]

            sentiment = (
                "positive" if label == "positive"
                else "negative" if label == "negative"
                else "neutral"
            )

            summary = ReviewSummarize(
                target_id="anthracite_cafe",         # 고정 or 인자로 받을 수 있음
                target_type="cafe",
                sentiment=sentiment,
                content=content
            )
            db.add(summary)

        db.commit()
        print("✅ 분석 및 저장 완료")

    except Exception as e:
        db.rollback()
        print("❌ 오류 발생:", e)
    finally:
        db.close()
