import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# Elasticsearch 주소
load_dotenv()
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL")

def fetch_data_from_elasticsearch():
    """
    Elasticsearch에서 당일자의 혼잡도 데이터를 조회

    Returns:
        dict or None: Elasticsearch로부터 받아온 JSON 데이터. 실패 시 None 반환
    """
    current_date = datetime.now()
    index_name = f"seoul_citydata_congestion_{current_date.year}{current_date.month:02d}{current_date.day:02d}"
    url = f"{ELASTICSEARCH_URL}/{index_name}/_search"

    query = {
        "query": { "match_all": {} },
        "_source": [
            "congestion.area_nm",
            "congestion.area_congest_lvl",
            "congestion.area_congest_msg",
            "congestion.fcst_ppltn.fcst_time",
            "congestion.fcst_ppltn.fcst_congest_lvl"
        ],
        "size": 120
    }

    try:
        response = requests.get(url, json=query)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def convert_to_sentence(doc, current_date):
    """
    Elasticsearch 문서를 자연어 요약 텍스트로 변환 (혼잡 시간 필터링)

    Args:
        doc (dict): Elasticsearch의 단일 document
        current_date (datetime): 현재 날짜 정보

    Returns:
        str or None: 요약 문장 (혼잡 시간이 있을 경우), 없으면 None
    """
    source = doc.get("_source", {})
    congestion = source.get("congestion", {})

    area_name = congestion.get("area_nm", "알 수 없음")
    current_level = congestion.get("area_congest_lvl", "")
    fcst_ppltn = congestion.get("fcst_ppltn", [])

    # 붐빔 예측 시간 필터링
    congested_times = [
        entry.get("fcst_time", "")[-5:]
        for entry in fcst_ppltn
        if entry.get("fcst_congest_lvl", "") == "붐빔"
    ]

    # 현재 붐빔이면 현재 시간도 추가
    if current_level == "붐빔" and fcst_ppltn:
        first_time = fcst_ppltn[0].get("fcst_time", "")[-5:]
        if first_time:
            hour = int(first_time.split(":")[0]) - 1
            if hour < 0:
                hour += 24
            congested_times.insert(0, f"{hour:02d}:00")

    if not congested_times:
        return None

    # 시간들 정리
    hour_list = []
    for t in congested_times:
        if ":" in t:
            hour_part = t.split(":")[0]
            hour_int = int(hour_part)
            hour_list.append(f"{hour_int}시" if hour_int != 0 else "0시")
        else:
            hour_list.append(t)  # 안전망

    date_str = f"{current_date.year}년 {current_date.month}월 {current_date.day}일"
    return f"{date_str}, {area_name}는 {', '.join(hour_list)}에 매우 혼잡합니다."

def save_congestion_to_json() -> None:
    """
    Elasticsearch에서 데이터를 가져와 혼잡도 요약 문장을 생성하고
    data 폴더에 'congestion_texts_YYYYMMDD.json' 형식으로 저장합니다.
    """
    current_date = datetime.now()
    data = fetch_data_from_elasticsearch()
    summaries = []

    if data:
        for doc in data.get("hits", {}).get("hits", []):
            natural_sentence = convert_to_sentence(doc, current_date)
            if natural_sentence:
                summaries.append(natural_sentence)

    # 데이터가 아예 없거나, 요약 결과가 없는 경우 메시지 추가
    if not summaries:
        summaries.append("혼잡도 데이터가 없습니다.")

    os.makedirs("data", exist_ok=True)
    file_suffix = current_date.strftime("%Y%m%d")
    output_path = os.path.join("data", f"congestion_texts_{file_suffix}.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=4)

    print(f"혼잡도 요약 문장 저장 완료: {output_path}")