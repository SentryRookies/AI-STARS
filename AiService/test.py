import os
from groq import Groq
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 예시 데이터
review = "직원들이 친절하고 방도 매우 깨끗했어요."
keyword_list = ["청결", "서비스", "맛", "가격", "위치", "시설", "분위기"]

# 프롬프트 구성
prompt = f"""
"{review}" 리뷰에 가장 적합한 키워드를 다음 목록에서 하나만 골라줘.
{', '.join(keyword_list)}

답변은 목록에 있는 키워드 하나만 출력해줘.
"""

# Groq API 호출
response = groq_client.chat.completions.create(
    messages=[{"role": "user", "content": prompt}],
    model="llama3-8b-8192"
)

# 응답에서 키워드 추출
extracted_keyword = response.choices[0].message.content.strip()

# 예외 처리
if extracted_keyword not in keyword_list:
    extracted_keyword = "기타"

# 결과 출력
print(f"추출된 키워드: {extracted_keyword}")
