import asyncio
from playwright.async_api import async_playwright
import csv
import datetime
import os
from sqlalchemy import create_engine, text

# DB 연결 정보
DB_URL = "postgresql://postgres:example@k8s-default-postgres-2cdafece7a-ac1876b9c7d705f9.elb.ap-northeast-2.amazonaws.com:5432/stars_db"
# tables = ["accommodation", "attraction", "cafe", "restaurant"]
tables = ["accommodation"]
MAX_REVIEWS = 100
MIN_LENGTH = 10

# row에서 id 추출
def get_row_id(row, table_name):
    return getattr(row, f"{table_name}_id")

# 크롤링 대상 가져오기
def load_targets(resume_from_id=None):
    crawl_targets = []
    engine = create_engine(DB_URL)
    with engine.connect() as connection:
        for table in tables:
            result = connection.execute(text(f"SELECT {table}_id, kakaomap_url FROM {table}"))
            for row in result:
                if not row.kakaomap_url:
                    continue
                crawl_targets.append({
                    "table": table,
                    "id": get_row_id(row, table),
                    "kakaomap_url": row.kakaomap_url
                })
    if resume_from_id:
        for i, item in enumerate(crawl_targets):
            if item["table"] == "accommodation" and item["id"] == resume_from_id:
                print(f"🔁 ID {resume_from_id} 이후부터 재시작합니다 (index {i+1}부터)")
                return crawl_targets[i + 1:]  # 해당 ID 다음 인덱스부터 반환
    return crawl_targets

# 크롤러 실행 (url별)
async def run_crawler(url, table, item_id):
    now = datetime.datetime.now()
    results = []
    save_dir = "./data"
    os.makedirs(save_dir, exist_ok=True)
    file_name = f"{table}_{item_id}_{now.strftime('%Y%m%d_%H%M')}.csv"
    file_path = os.path.join(save_dir, file_name)

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url)
            await page.wait_for_timeout(3000)

            # 정렬 클릭
            try:
                await page.click("button.btn_sort")
                await page.wait_for_timeout(100)
                await page.click("a.link_sort")
            except:
                pass

            # 스크롤
            for _ in range(10):
                await page.evaluate("window.scrollBy(0, document.body.scrollHeight);")
                await page.wait_for_timeout(1000)

            # 더보기 버튼
            more_buttons = await page.query_selector_all("span.btn_more")
            for button in more_buttons:
                try:
                    if "더보기" in await button.inner_text():
                        await button.click()
                        await page.wait_for_timeout(500)
                except:
                    continue

            # 리뷰 수집
            review_elements = await page.query_selector_all("p.desc_review")
            count = 0
            for review in review_elements:
                text = (await review.inner_text()).strip().replace("\n", " ")
                if len(text) >= MIN_LENGTH:
                    results.append({"content": text})
                    count += 1
                if count >= MAX_REVIEWS:
                    break

            await browser.close()

        # 저장
        if len(results) >= 10:
            with open(file_path, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=["content"])
                writer.writeheader()
                writer.writerows(results)
            print(f"✅ [{table} - {item_id}] {len(results)}개 리뷰 저장 완료: {file_path}")
        else:
            print(f"⚠️  [{table} - {item_id}] 리뷰 개수 {len(results)}개로 저장하지 않음")

    except Exception as e:
        print(f"❌ [{table} - {item_id}] 에러 발생: {e}")

# 전체 실행
async def main():
    # targets = load_targets()
    # 여기서 원하는 기준 ID 넣기
    targets = load_targets(resume_from_id=391589894)

    for target in targets:
        url_with_comment = target["kakaomap_url"] + "#comment"
        await run_crawler(
            url=url_with_comment,
            table=target["table"],
            item_id=target["id"]
        )
        await asyncio.sleep(2)  # 너무 빠르면 차단될 수 있으니 잠깐 쉬기

if __name__ == "__main__":
    asyncio.run(main())
