from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import atexit
import os
import pandas as pd
import json
from app.database import SessionLocal
from app.model import Review_summarize
from batch.emotion_model import analyze_reviews
from batch.keyword_model import extract_top_keywords

# 마지막 작업 Data 확인
def load_last_processed(path="last_processed.json"):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f).get("last_processed")
    return None

# 마지막 작업 Data 저장
def save_last_processed(filename, path="last_processed.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"last_processed": filename}, f)

# 키워드 추출 프로세싱
def crawl_and_analyze():
    print("📦 [스케줄러] CSV 읽기 + 분석 시작")
    db = SessionLocal()
    data_dir = "./data"

    last_processed = load_last_processed()
    files = sorted(f for f in os.listdir(data_dir) if f.endswith(".csv"))

    try:
        skip = True if last_processed else False

        for file_name in files:
            if skip:
                if file_name == last_processed:
                    skip = False
                continue

            file_path = os.path.join(data_dir, file_name)
            print(f"📂 파일 분석 시작: {file_path}")

            # ✅ target_type, target_id 추출
            name_parts = file_name.replace(".csv", "").split("_")
            if len(name_parts) < 3:
                print(f"⚠️ 파일 이름 형식 오류: {file_name}")
                continue

            target_type = name_parts[0]
            target_id = name_parts[1]

            df = pd.read_csv(file_path, encoding="utf-8-sig")
            df = df.dropna(subset=["content"])
            reviews = [{"content": text} for text in df["content"]]

            validated_data = analyze_reviews(reviews)
            validated_data = [r for r in validated_data if r and all(k in r for k in ("text", "label", "score"))]

            print(f"검증된 데이터 수: {len(validated_data)}")
            analyzed_df = pd.DataFrame(validated_data)

            pos_keywords, neg_keywords = extract_top_keywords(validated_data)

            pos_count = analyzed_df[analyzed_df["label"] == "positive"].shape[0]
            neg_count = analyzed_df[analyzed_df["label"] == "negative"].shape[0]

            content_summary = (
                f"[긍정 키워드] {', '.join(pos_keywords)}\n"
                f"[부정 키워드] {', '.join(neg_keywords)}\n"
                f"[긍정 라벨 수] {pos_count}\n"
                f"[부정 라벨 수] {neg_count}"
            )

            # 기존 데이터 조회
            existing = db.query(Review_summarize).filter_by(
                target_id=target_id,
                target_type=target_type
            ).first()

            # 기존 데이터 존재 -> 기존 항목 업데이트
            if existing:
                existing.content = content_summary
                print(f"기존 항목 업데이트: {target_type}, {target_id}")
            # 기존 데이터 존재 X -> 새로 생성
            else:
                summary = Review_summarize(
                    target_id=target_id,
                    target_type=target_type,
                    content=content_summary
                )
                db.add(summary)
                print(f"새 항목 추가: {target_type}, {target_id}")
            db.commit()
            print(f"{file_name} 분석 및 저장 완료")

            # 파일 처리 후 기록
            save_last_processed(file_name)

    except Exception as e:
        db.rollback()
        import traceback
        print("오류 발생:", repr(e))
        traceback.print_exc()
    finally:
        db.close()

# 메인 스케줄러 함수
def start_scheduler():
    scheduler = BackgroundScheduler()
    # 스케줄러 일정 조절
    scheduler.add_job(crawl_and_analyze, CronTrigger(hour=10, minute=0))
    scheduler.start()
    print("APScheduler 시작됨")
    atexit.register(lambda: scheduler.shutdown())


if __name__ == "__main__":
    start_scheduler()
