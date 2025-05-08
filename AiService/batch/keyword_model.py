# batch/keyword/keyword_extractor.py
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from typing import List, Dict, Tuple

# 1. 임베딩 모델 로드
model = SentenceTransformer("jhgan/ko-sbert-nli")

# 2. 키워드 매핑 (positive/negative)
positive_keyword_mapping = {
    "전반적": [
        "전반적으로 좋았어요,",
        "다음에 다시 오고 싶어요",
        "이 장소를 추천해요"
    ],
    "공간": [
        "공간이 쾌적했어요.",
        "공기가 맑았어요."
    ],
    "위생": [
        "전체적으로 깨끗했어요.",
        "청소가 잘 되어 있었어요.",
        "위생 상태가 좋았어요."
    ],
    "재미": [
        "아이들이 즐거워했어요.",
        "놀 거리가 많았어요.",
        "볼 거리가 많았어요"
    ],
    "음식": [
        "음식이 정말 맛있었어요.",
        "음식의 맛이 훌륭했어요.",
        "음식의 맛이 기대 이상이었어요.",
        "이 음식을 추천해요",
        "음식 양이 충분해요.",
        "음식 양이 적당해요",
        "배부르게 먹었어요."
    ],
    "분위기": [
        "분위기가 아늑했어요.",
        "분위기가 매우 편안했어요.",
        "조용한 분위기였어요.",
        "분위기가 좋아요."
    ],
    "서비스": [
        "서비스가 정말 훌륭했어요.",
        "직원들이 친절하고 응대가 좋았어요.",
        "응대가 정중하고 편안했어요.",
        "안내가 잘 되어 있어서 편리했어요."
    ],
    "선택지/메뉴": [
        "메뉴가 다양하고 선택의 폭이 넓었어요.",
        "메뉴가 풍성하고 만족스러웠어요.",
        "다양한 메뉴가 있어서 고르기 좋았어요."
    ],
    "가격": [
        "가격이 합리적이었어요.",
        "가격 대비 만족도가 높았어요.",
        "가격이 적당해서 만족했어요."
    ],
    "대기시간": [
        "대기시간이 짧아요",
        "대기시간이 빠르게 지나갔어요."
    ],
    "전망/경치": [
        "전망이 멋졌어요.",
        "경치가 탁 트여서 좋았어요.",
        "전망이 훌륭했어요."
    ],
    "접근성": [
        "위치가 정말 편리했어요.",
        "찾기 쉬운 위치였어요.",
        "접근하기 편했어요."
    ],
    "주차": [
        "주차 공간이 충분했어요",
        "주차가 아주 쉬웠어요.",
        "주차장이 넓어서 편하게 주차했어요."
    ],
    "전시/관람": [
        "관람하기 좋았어요.",
        "전시가 잘 구성되어 있어요.",
        "관람할 시간이 잘 배분되어 있어요.",
        "사진이 잘 나와요."
    ],
    "혼잡": [
        "혼잡하지 않아요.",
        "사람이 많지 않아요.",
        "사람이 없어요.",
        "관광객이 많지 않아요"
    ],
    "시설": [
        "편의시설이 잘 갖춰져 있어요.",
        "시설이 잘 관리되어 있었어요.",
        "편의시설이 많아 이용이 편리했어요."
    ],
    "예약": [
        "예약하기 편해요",
        "예약 시스템이 잘 갖추어져 있어요"
    ],
    "날씨":[
        "날씨가 좋았어요",
        "바람이 시원하게 불었어요."
    ]
}

negative_keyword_mapping = {
    "전반적": [
        "전반적으로 좋지 않았어요.",
        "다음에 다시 오고 싶지 않아요",
        "전반적으로 아쉬워요"
    ],
    "공간": [
        "공간이 좁아요.",
        "공기가 탁해요.",
        "공간 내부가 너무 추워요",
        "공간 내부가 너무 더워요"
    ],
    "위생": [
        "전체적으로 더러웠어요.",
        "청소가 잘 되어 있지 않았어요.",
        "위생 상태가 좋지 않았어요.",
        "깨끗했으면 좋겠어요",
        "벌레가 많아요"
    ],
    "재미": [
        "놀 거리가 부족했어요.",
        "볼 거리가 부족했어요"
    ],
    "음식": [
        "음식이 맛이 별로였어요.",
        "음식의 맛이 기대 이하였어요.",
        "음식이 짜요.",
        "음식의 염도가 높았어요",
        "음식이 싱거워요.",
        "음식의 맛이 그냥 그래요." ,
        "음식 양이 적어요.",
        "음식 양이 많았으면 좋겠어요"
    ],
    "분위기": [
        "분위기가 너무 어두웠어요.",
        "시끄러운 분위기였어요.",
        "조용했으면 좋겠어요"
    ],
    "서비스": [
        "서비스가 불친절했어요.",
        "직원들의 응대가 나빴어요.",
        "응대가 느리고 불편했어요.",
        "친절했으면 좋겠어요",
        "안내가 부족해서 찾기 힘들었어요."
    ],
    "선택지/메뉴": [
        "메뉴가 제한적이었어요.",
        "메뉴가 부족했어요.",
        "메뉴가 없어서 아쉬웠어요.",
        "선택지가 다양했으면 좋겠어요"
    ],
    "가격": [
        "가격이 비쌌어요.",
        "가격 대비 만족도가 낮았어요.",
        "가성비가 좋지 않았어요.",
        "추가 비용이 발생했어요"
    ],
    "대기시간": [
        "대기시간이 길었어요.",
        "대기시간이 오래 걸렸어요."
    ],
    "전망/경치": [
        "전망이 좋지 않았어요.",
        "경치가 가려져 있었어요."
    ],
    "접근성": [
        "위치가 불편했어요.",
        "위치가 멀었어요.",
        "위치가 외졌어요."
    ],
    "주차": [
        "주차 공간이 부족했어요.",
        "주차가 어려웠어요.",
        "주차장이 협소했어요.",
        "주차가 편리했으면 좋겠어요"
    ],
    "전시/관람": [
        "관람 환경이 불편했어요.",
        "전시가 제대로 구성되지 않았어요.",
        "관람 시간이 부족했어요.",
        "관람 환경이 좋았으면 좋겠어요",
        "사진이 잘 안 나와요"
    ],
    "혼잡": [
        "혼잡했어요.",
        "사람이 많았어요.",
        "혼잡하지 않았으면 좋겠어요",
        "관광객이 많아요",
        "자리가 없어요"
    ],
    "시설": [
        "편의시설이 부족했어요.",
        "시설이 제대로 관리되지 않았어요.",
        "시설이 불편해요",
        "가구가 불편해요",
        "시설이 편리했으면 좋겠어요"
    ],
    "예약": [
        "예약이 쉽지 않아요",
        "예약 방식이 불편해요",
        "예약이 편리해졌으면 좋겠어요"
    ],
    "날씨":[
        "날씨가 좋지 않았어요",
        "날씨가 추워요",
        "날씨가 더워요",
        "바람이 너무 강해요."
    ],
    "피로": [
        "체력적으로 힘들었어요.",
        "체력적으로 지쳤어요.",
        "걸음이 너무 힘들었어요."
    ]
}


# 3. 키워드 매칭 함수
def get_top_keyword_and_score(text: str, keyword_dict: Dict) -> pd.Series:
    text_embedding = model.encode(text, convert_to_tensor=True)
    scores = {}
    best_sentence = ""
    best_score = -1

    for keyword, reps in keyword_dict.items():
        rep_embeddings = model.encode(reps, convert_to_tensor=True)
        score = util.pytorch_cos_sim(text_embedding, rep_embeddings).max().item()
        scores[keyword] = score

        if score > best_score:
            best_score = score
            best_sentence = reps[reps.index(
                max(reps, key=lambda x: util.pytorch_cos_sim(
                    text_embedding, model.encode(x, convert_to_tensor=True)).item()
                )
            )]

    top_keyword = max(scores, key=scores.get)
    return pd.Series([top_keyword, best_sentence, best_score])

# 4. 리뷰 리스트로부터 키워드 추출
def extract_top_keywords(analyzed_data: List[Dict], save: bool = False, prefix: str = "result") -> Tuple[List[str], List[str]]:
    df = pd.DataFrame(analyzed_data)

    # 감정 필터링
    positive_df = df[df["label"] == "positive"].copy()
    negative_df = df[df["label"] == "negative"].copy()

    # 키워드 추출 결과 저장용
    positive_keywords = []
    negative_keywords = []

    # 긍정 리뷰 키워드 추출
    # positive_results = positive_df["text"].apply(lambda x: get_top_keyword_and_score(x, positive_keyword_mapping))
    # positive_df["keyword"] = positive_results.apply(lambda x: x[0] if isinstance(x, (list, tuple, pd.Series)) else None)
    # positive_df["similar_sentence"] = positive_results.apply(lambda x: x[1] if isinstance(x, (list, tuple, pd.Series)) else None)
    # positive_df["score"] = positive_results.apply(lambda x: x[2] if isinstance(x, (list, tuple, pd.Series)) else None)

    # 부정 리뷰 키워드 추출
    # negative_results = negative_df["text"].apply(lambda x: get_top_keyword_and_score(x, negative_keyword_mapping))
    # negative_df["keyword"] = negative_results.apply(lambda x: x[0] if isinstance(x, (list, tuple, pd.Series)) else None)
    # negative_df["similar_sentence"] = negative_results.apply(lambda x: x[1] if isinstance(x, (list, tuple, pd.Series)) else None)
    # negative_df["score"] = negative_results.apply(lambda x: x[2] if isinstance(x, (list, tuple, pd.Series)) else None)

    # 긍정 리뷰 키워드 추출
    positive_results = positive_df["text"].apply(lambda x: get_top_keyword_and_score(x, positive_keyword_mapping))
    positive_results_df = positive_results.apply(pd.Series)
    positive_results_df.columns = ["keyword", "similar_sentence", "score"]
    positive_df = pd.concat([positive_df, positive_results_df], axis=1)

    # 부정 리뷰 키워드 추출
    negative_results = negative_df["text"].apply(lambda x: get_top_keyword_and_score(x, negative_keyword_mapping))
    negative_results_df = negative_results.apply(pd.Series)
    negative_results_df.columns = ["keyword", "similar_sentence", "score"]
    negative_df = pd.concat([negative_df, negative_results_df], axis=1)

    # 상위 키워드 추출
    top_pos = positive_df["keyword"].value_counts().head(5)
    top_neg = negative_df["keyword"].value_counts().head(5)

    pos_list = top_pos.index.tolist()
    neg_list = [k for k in top_neg.index if k not in pos_list]
    # 키워드 제외(날씨, 피로)
    if "날씨" in pos_list:
        pos_list.remove("날씨")
    if "날씨" in neg_list:
        neg_list.remove("날씨")
    if "피로" in neg_list:
        neg_list.remove("피로")

    # 중복된 키워드 처리: 긍정과 부정에 모두 있는 키워드에서 개수가 적은 쪽의 키워드를 제외
    for keyword in pos_list[:]:
        if keyword in neg_list:
            # 긍정과 부정에서 해당 키워드의 개수 비교
            positive_count = top_pos.get(keyword, 0)
            negative_count = top_neg.get(keyword, 0)

            if positive_count < negative_count:
                # 긍정에서 해당 키워드 제거
                pos_list.remove(keyword)
            elif positive_count > negative_count:
                # 부정에서 해당 키워드 제거
                neg_list.remove(keyword)
            else:
                # 개수가 같으면 긍부정 모두 제거
                pos_list.remove(keyword)
                neg_list.remove(keyword)

    # 카운트가 3개 이하인 키워드 제거
    pos_list = [keyword for keyword in pos_list if top_pos[keyword] > 2]
    neg_list = [keyword for keyword in neg_list if top_neg[keyword] > 2]
            

    if len(neg_list) < 5:
        remaining = [k for k in top_neg.index if k not in neg_list and k not in pos_list]
        for k in remaining:
            if len(neg_list) < 5:
                neg_list.append(k)

    # if save:
    #     positive_df.to_excel(f"{prefix}_positive.xlsx", index=False)
    #     negative_df.to_excel(f"{prefix}_negative.xlsx", index=False)

    print("📈 긍정 키워드:", pos_list)
    print("📉 부정 키워드:", neg_list)

    return pos_list, neg_list
