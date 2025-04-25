# 크롤링 및 감정분류 후 키워드 추출 동작 1달에 한번 동작 스케줄링

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import atexit

def crawl_and_analyze():
    print("📦 [스케줄러] 리뷰 크롤링 → 감정분석 → 키워드 추출 → DB 저장 실행")

    # 여기에 실제 작업 함수 연결할 예정


def start_scheduler():
    scheduler = BackgroundScheduler()

    # 매달 1일 오전 3시에 실행 (실 서비스용)
    scheduler.add_job(crawl_and_analyze, CronTrigger(day=1, hour=3, minute=0))


    scheduler.start()
    print("🕒 APScheduler 시작됨")

    # 서버 종료 시 스케줄러 정지
    atexit.register(lambda: scheduler.shutdown())