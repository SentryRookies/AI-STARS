import asyncio
from playwright.async_api import async_playwright
from openpyxl import Workbook
import datetime

MAX_REVIEWS = 100
MIN_LENGTH = 10
URL = "https://m.place.naver.com/place/1932878505/review/visitor?reviewSort=recent"

async def run():
    now = datetime.datetime.now()
    xlsx = Workbook()
    sheet = xlsx.active
    sheet.title = "reviews"
    sheet.append(["content"])

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(URL)
        await page.wait_for_timeout(3000)


        # 더보기 버튼 반복 클릭
        for _ in range(30):
            try:
                await page.click("a.fvwqf", timeout=1000)
                print("더보기클릭")
                await page.wait_for_timeout(1000)
            except:
                break

        # 정확히 div.pui__vn15t2 > a[role=button] 구조에서 텍스트 추출
        review_boxes = await page.query_selector_all("div.pui__vn15t2 a[role='button']")
        count = 0

        for box in review_boxes:
            text = (await box.inner_text()).strip().replace("\n", " ")
            if len(text) >= MIN_LENGTH:
                sheet.append([text])
                count += 1
            if count >= MAX_REVIEWS:
                break

        await browser.close()
        xlsx.save(f"seoulBotanicalReviews.xlsx")

asyncio.run(run())
