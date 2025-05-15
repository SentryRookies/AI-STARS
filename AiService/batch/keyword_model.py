# batch/keyword/keyword_extractor.py
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from typing import List, Dict, Tuple
from keyword_mapping import positive_keyword_mapping, negative_keyword_mapping

# 1. 임베딩 모델 로드
model = SentenceTransformer("jhgan/ko-sbert-nli")

# 2. 키워드 매칭 함수
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

# 3. 리뷰 리스트로부터 키워드 추출
def extract_top_keywords(analyzed_data: List[Dict], save: bool = False, prefix: str = "result") -> Tuple[List[str], List[str]]:
    df = pd.DataFrame(analyzed_data)

    # 감정 필터링
    positive_df = df[df["label"] == "positive"].copy()
    negative_df = df[df["label"] == "negative"].copy()

    # 키워드 추출 결과 저장용
    positive_keywords = []
    negative_keywords = []

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
            positive_count = top_pos.get(keyword, 0)
            negative_count = top_neg.get(keyword, 0)

            if positive_count < negative_count:
                pos_list.remove(keyword)

            elif positive_count > negative_count:
                neg_list.remove(keyword)

            # 개수가 같으면 긍부정 모두 제거
            else:
                pos_list.remove(keyword)
                neg_list.remove(keyword)

    # 중복되는 의견이 적은 키워드 제거(카운트 3개 이하)
    pos_list = [keyword for keyword in pos_list if top_pos[keyword] > 2]
    neg_list = [keyword for keyword in neg_list if top_neg[keyword] > 2]
            

    if len(neg_list) < 5:
        remaining = [k for k in top_neg.index if k not in neg_list and k not in pos_list]
        for k in remaining:
            if len(neg_list) < 5:
                neg_list.append(k)

    print("긍정 키워드:", pos_list)
    print("부정 키워드:", neg_list)

    return pos_list, neg_list
