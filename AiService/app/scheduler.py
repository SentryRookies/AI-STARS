from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import atexit

import os
import pandas as pd

from app.database import SessionLocal
from app.model import ReviewSummarize

from batch.emotionModel import analyzeReviews
from batch.keywordModel import extractTopKeywords

def crawlAndAnalyze(targetId="anthraciteCafe", targetType="cafe"):
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
                
                validated_data = analyzeReviews(reviews)
                validated_data = [r for r in validated_data if r and all(k in r for k in ("text", "label", "score"))]

                print(f"✅ 검증된 데이터 수: {len(validated_data)}")

                analyzed_df = pd.DataFrame(validated_data)

                extractTopKeywords(validated_data)

                for idx, row in analyzed_df.iterrows():
                    label = row["label"]
                    content = row["text"]
                    sentiment = (
                        "positive" if label == "positive"
                        else "negative" if label == "negative"
                        else "neutral"
                    )

                    summary = ReviewSummarize(
                        target_id=targetId,
                        target_type=targetType,
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


# 본 프로젝트 스케줄러 : 매달 1일 실행d
def startScheduler():
    scheduler = BackgroundScheduler()

    # 매달 1일 오전 3시
    scheduler.add_job(crawlAndAnalyze, CronTrigger(day=1, hour=3, minute=0))

    scheduler.start()
    print("🕒 APScheduler 시작됨")

    atexit.register(lambda: scheduler.shutdown())

# 테스팅요 스케줄러 : 1분마다
# def startScheduler():
#     scheduler = BackgroundScheduler()

#     # ✅ 테스트용: 1분마다 동작
#     scheduler.add_job(crawlAndAnalyze, CronTrigger(minute="*/1"))

#     scheduler.start()
#     print("🕒 APScheduler 시작됨 (테스트용 1분마다 실행)")

#     atexit.register(lambda: scheduler.shutdown())

# (메인 서버 파일)
if __name__ == "__main__":
    startScheduler()