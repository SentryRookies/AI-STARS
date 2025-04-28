# batch/keyword/keyword_extractor.py
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from typing import List

# 1. 임베딩 모델 로드
model = SentenceTransformer("jhgan/ko-sbert-nli")

# 2. 키워드 매핑 (positive/negative)
positiveKeywordMapping = { ... }  
negativeKeywordMapping = { ... }

# 3. 키워드 매칭 함수
def getTopKeywordAndScore(text: str, keywordDict: dict) -> pd.Series:
    textEmbedding = model.encode(text, convert_to_tensor=True)
    scores = {}
    bestSentence = ""
    bestScore = -1

    for keyword, reps in keywordDict.items():
        repEmbeddings = model.encode(reps, convert_to_tensor=True)
        score = util.pytorch_cos_sim(textEmbedding, repEmbeddings).max().item()
        scores[keyword] = score

        if score > bestScore:
            bestScore = score
            bestSentence = reps[reps.index(
                max(reps, key=lambda x: util.pytorch_cos_sim(
                    textEmbedding, model.encode(x, convert_to_tensor=True)).item()
                )
            )]

    topKeyword = max(scores, key=scores.get)
    return pd.Series([topKeyword, bestSentence, bestScore])

# 4. 리뷰 리스트로부터 키워드 추출
def extractTopKeywords(analyzedData: list[dict], save: bool = False, prefix: str = "result") -> tuple[list, list]:
    df = pd.DataFrame(analyzedData)

    # 감정 필터링
    positive_df = df[df["label"] == "positive"].copy()
    negative_df = df[df["label"] == "negative"].copy()

    # 키워드 추출 결과 저장용
    positive_keywords = []
    negative_keywords = []

    # 긍정 리뷰 키워드 추출
    positive_results = positive_df["text"].apply(lambda x: getTopKeywordAndScore(x, positiveKeywordMapping))
    positive_df["keyword"] = positive_results.apply(lambda x: x[0] if isinstance(x, (list, tuple)) else None)
    positive_df["similar_sentence"] = positive_results.apply(lambda x: x[1] if isinstance(x, (list, tuple)) else None)
    positive_df["score"] = positive_results.apply(lambda x: x[2] if isinstance(x, (list, tuple)) else None)

    # 부정 리뷰 키워드 추출
    negative_results = negative_df["text"].apply(lambda x: getTopKeywordAndScore(x, negativeKeywordMapping))
    negative_df["keyword"] = negative_results.apply(lambda x: x[0] if isinstance(x, (list, tuple)) else None)
    negative_df["similar_sentence"] = negative_results.apply(lambda x: x[1] if isinstance(x, (list, tuple)) else None)
    negative_df["score"] = negative_results.apply(lambda x: x[2] if isinstance(x, (list, tuple)) else None)

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
