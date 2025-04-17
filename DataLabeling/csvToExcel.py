import pandas as pd

# CSV 파일 경로
csv_path = "DeoksugungReviewspnn.csv"

# 저장할 Excel 파일 경로
excel_path = ".DeoksugungReviews.xlsx"

# CSV 파일 읽기
df = pd.read_csv(csv_path)

# Excel 파일로 저장 (엑셀 writer에 openpyxl 엔진 사용)
df.to_excel(excel_path, index=False, engine='openpyxl')

print(f"변환 완료: {excel_path}")