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

def load_last_processed(path="last_processed.json"):
    """
        마지막으로 처리된 파일명 불러오기

        Args:
            path (str): 저장된 JSON 파일 경로

        Returns:
            str: 마지막 처리된 파일 이름 (없으면 None)
        """
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f).get("last_processed")
    return None

def save_last_processed(filename, path="last_processed.json"):
    """
        처리 완료된 마지막 파일명을 기록

        Args:
            filename (str): 마지막으로 처리한 파일 이름
            path (str): 기록을 저장할 JSON 경로
        """
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"last_processed": filename}, f)

# 전역 DB 세션 객체
db = None

def crawl_and_analyze():
    """
        데이터 디렉토리의 CSV 파일을 주기적으로 분석하여 DB에 저장한다.

        수행 작업:
            - 분석되지 않은 CSV 파일을 탐색
            - 파일명에서 target_type, target_id 추출
            - 리뷰 텍스트 분석 (문장/절 분리 및 감정 분류) 'analyze_reviews'
            - 키워드 추출 (긍정/부정) 'extract_top_keywords'
            - 분석 요약을 DB에 저장 또는 업데이트
            - 마지막 처리 파일명 저장

        예외 발생 시 롤백 및 에러 출력
        """
    print(" [스케줄러] CSV 읽기 + 분석 시작")
    global db
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
            print(f" 파일 분석 시작: {file_path}")

            #  target_type, target_id 추출
            name_parts = file_name.replace(".csv", "").split("_")
            if len(name_parts) < 3:
                print(f" 파일 이름 형식 오류: {file_name}")
                continue

            target_type = name_parts[0]
            target_id = name_parts[1]

            df = pd.read_csv(file_path, encoding="utf-8-sig")
            df = df.dropna(subset=["content"])
            reviews = [{"content": text} for text in df["content"]]

            validated_data = analyze_reviews(reviews)
            validated_data = [r for r in validated_data if r and all(k in r for k in ("text", "label", "score"))]

            print(f" 검증된 데이터 수: {len(validated_data)}")
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

            if existing:
                existing.content = content_summary
                print(f" 기존 항목 업데이트: {target_type}, {target_id}")
            else:
                summary = Review_summarize(
                    target_id=target_id,
                    target_type=target_type,
                    content=content_summary
                )
                db.add(summary)
                print(f" 새 항목 추가: {target_type}, {target_id}")
            db.commit()
            print(f" {file_name} 분석 및 저장 완료")

            #  파일 처리 후 기록
            save_last_processed(file_name)

    except Exception as e:
        db.rollback()
        import traceback
        print(" 오류 발생:", repr(e))
        traceback.print_exc()
    finally:
        db.close()

def start_scheduler():
    """
        APScheduler를 시작하여 `crawl_and_analyze`를 매달 1일 오전 1시에 실행한다.
        애플리케이션 종료 시 스케줄러 종료 처리도 포함된다.
    """
    global db
    db = SessionLocal()  # 시작 시 DB 연결
    scheduler = BackgroundScheduler()
    scheduler.add_job(crawl_and_analyze, CronTrigger(day=1, hour=1, minute=00))
    scheduler.start()
    print(" APScheduler 시작됨")

    # 종료 시 DB도 닫기
    def shutdown():
        print(" 스케줄러 종료: DB 세션 닫기")
        scheduler.shutdown()
        db.close()

    atexit.register(shutdown)

if __name__ == "__main__":
    start_scheduler()
