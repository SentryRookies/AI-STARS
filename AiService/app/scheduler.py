from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import atexit
import os
import pandas as pd

from app.database import SessionLocal
from app.model import Review_summarize

from batch.emotion_model import analyze_reviews
from batch.keyword_model import extract_top_keywords

def crawl_and_analyze(target_id="anthracite_cafe", target_type="cafe"):
    print("📦 [스케줄러] CSV 읽기 + 분석 시작")

    db = SessionLocal()
    data_dir = "./data"

    try:
        for file_name in os.listdir(data_dir):
            if file_name.endswith(".csv"):
                file_path = os.path.join(data_dir, file_name)
                print(f"📂 파일 분석 시작: {file_path}")

                df = pd.read_csv(file_path, encoding="utf-8-sig")
                df = df.dropna(subset=["content"])
                reviews = [{"content": text} for text in df["content"]]
                
                validated_data = analyze_reviews(reviews)
                validated_data = [r for r in validated_data if r and all(k in r for k in ("text", "label", "score"))]

                print(f"✅ 검증된 데이터 수: {len(validated_data)}")

                analyzed_df = pd.DataFrame(validated_data)

                extract_top_keywords(validated_data)

                for idx, row in analyzed_df.iterrows():
                    label = row["label"]
                    content = row["text"]
                    sentiment = (
                        "positive" if label == "positive"
                        else "negative" if label == "negative"
                        else "neutral"
                    )

                    summary = Review_summarize(
                        target_id=target_id,
                        target_type=target_type,
                        sentiment=sentiment,
                        content=content
                    )
                    db.add(summary)

                db.commit()
                print(f"✅ {file_name} 분석 및 저장 완료")

    except Exception as e:
        db.rollback()
        print("❌ 오류 발생:", e)
    finally:
        db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()

    # 매달 1일 오전 3시
    scheduler.add_job(crawl_and_analyze, CronTrigger(day=1, hour=3, minute=0))

    scheduler.start()
    print("🕒 APScheduler 시작됨")

    atexit.register(lambda: scheduler.shutdown())

# (메인 서버 파일에서 실행용)
if __name__ == "__main__":
    start_scheduler()
