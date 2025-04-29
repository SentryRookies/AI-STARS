# batch/keyword/keyword_extractor.py
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from typing import List, Dict, Tuple

# 1. 임베딩 모델 로드
model = SentenceTransformer("jhgan/ko-sbert-nli")

# 2. 키워드 매핑 (positive/negative)
positive_keyword_mapping = { ... }
negative_keyword_mapping = { ... }

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
    positive_results = positive_df["text"].apply(lambda x: get_top_keyword_and_score(x, positive_keyword_mapping))
    positive_df["keyword"] = positive_results.apply(lambda x: x[0] if isinstance(x, (list, tuple, pd.Series)) else None)
    positive_df["similar_sentence"] = positive_results.apply(lambda x: x[1] if isinstance(x, (list, tuple, pd.Series)) else None)
    positive_df["score"] = positive_results.apply(lambda x: x[2] if isinstance(x, (list, tuple, pd.Series)) else None)

    # 부정 리뷰 키워드 추출
    negative_results = negative_df["text"].apply(lambda x: get_top_keyword_and_score(x, negative_keyword_mapping))
    negative_df["keyword"] = negative_results.apply(lambda x: x[0] if isinstance(x, (list, tuple, pd.Series)) else None)
    negative_df["similar_sentence"] = negative_results.apply(lambda x: x[1] if isinstance(x, (list, tuple, pd.Series)) else None)
    negative_df["score"] = negative_results.apply(lambda x: x[2] if isinstance(x, (list, tuple, pd.Series)) else None)

    # 상위 키워드 추출
    top_pos = positive_df["keyword"].value_counts().head(5)
    top_neg = negative_df["keyword"].value_counts().head(5)

    pos_list = top_pos.index.tolist()
    neg_list = [k for k in top_neg.index if k not in pos_list]

    if len(neg_list) < 5:
        remaining = [k for k in top_neg.index if k not in neg_list and k not in pos_list]
        for k in remaining:
            if len(neg_list) < 5:
                neg_list.append(k)

    if save:
        positive_df.to_excel(f"{prefix}_positive.xlsx", index=False)
        negative_df.to_excel(f"{prefix}_negative.xlsx", index=False)

    print("📈 긍정 키워드:", pos_list)
    print("📉 부정 키워드:", neg_list)

    return pos_list, neg_list
