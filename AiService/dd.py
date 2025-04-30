from sqlalchemy import create_engine, text

# DB 연결 정보
DB_URL = "postgresql://postgres:example@k8s-default-postgres-8756371d73-960d1765a31c280e.elb.ap-northeast-2.amazonaws.com:5432/stars_db"

# 크롤링할 데이터 담을 리스트
crawl_targets = []

# 테이블 리스트
tables = ["accommodation", "attraction", "cafe", "restaurant"]

# row에서 id를 가져오는 함수
def get_row_id(row, table_name):
    id_column = f"{table_name}_id"
    return getattr(row, id_column)

# DB 연결
engine = create_engine(DB_URL)

# 연결 시작
with engine.connect() as connection:
    for table in tables:
        query = text(f"SELECT {table}_id, kakaomap_url FROM {table}")
        result = connection.execute(query)

        for row in result:
            if not row.kakaomap_url:  # None이거나 빈 문자열인 경우
                continue  # 추가하지 않고 스킵
            crawl_targets.append({
                "table": table,
                "id": get_row_id(row, table),
                "kakaomap_url": row.kakaomap_url
            })

# 결과 확인
for target in crawl_targets:
    print(target)

print(len(crawl_targets))

