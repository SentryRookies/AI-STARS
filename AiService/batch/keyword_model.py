# batch/keyword/keyword_extractor.py
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from typing import List, Dict, Tuple
import os
import json

# 임베딩 모델 로드
model = SentenceTransformer("jhgan/ko-sbert-nli")

# 키워드 매핑 JSON 불러오기
base_dir = os.path.dirname(__file__)
mapping_dir = os.path.join(base_dir, "keyword_mapping")

def load_json_mapping(file_name: str) -> dict:
    """
    긍정/부정 키워드를 정의한 JSON 파일을 불러와 딕셔너리 형태로 반환
    """
    path = os.path.join(mapping_dir, file_name)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

positive_keyword_mapping = load_json_mapping("positive_keyword_mapping.json")
negative_keyword_mapping = load_json_mapping("negative_keyword_mapping.json")

def get_top_keyword_and_score(text: str, keyword_dict: Dict) -> pd.Series:
    """
        입력 텍스트와 가장 유사한 키워드 및 대표 문장과 유사도를 반환한다.

        이 함수는 주어진 텍스트를 임베딩한 후, 제공된 키워드 딕셔너리 내 대표 문장들과의
        코사인 유사도를 계산한다. 가장 높은 유사도를 보인 키워드와 해당 문장을 추출하여 반환함.

        Args:
            text (str): 비교 대상이 되는 입력 텍스트
            keyword_dict (Dict[str, List[str]]): 키워드와 해당 키워드의 대표 문장 리스트를 가진 딕셔너리

        Returns:
            pd.Series:다음 항목을 포함하는 pd.Series 반환
                - top_keyword (str): 가장 유사한 키워드
                - best_sentence (str): 가장 유사한 대표 문장
                - best_score (float): 최고 유사도 점수 (0~1)
        """
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

def extract_top_keywords(analyzed_data: List[Dict], save: bool = False, prefix: str = "result") -> Tuple[List[str], List[str]]:
    """
       감정 분석된 절 데이터에서 긍정/부정 상위 키워드 추출

       이 함수는 분석된 텍스트 리스트를 긍정/부정 감정으로 분리한 뒤,
       각 문장에 대해 `get_top_keyword_and_score` 함수를 통해 가장 유사한 키워드를 매칭함.
       이후 등장 빈도를 기준으로 상위 키워드를 선정하며, 특정 키워드는 제외하거나 중복 처리를 통해 정제한다.

       Args:
           analyzed_data (List[Dict]): 감정 분석된 절 단위 데이터. 각 항목은 'text'와 'label' 키를 포함하여야 함.
           save (bool, optional): 결과를 엑셀 파일로 저장할지 여부 (기본값 False)
           prefix (str, optional): 저장 시 사용할 파일 이름 접두어 (기본값 "result")

       Returns:
           Tuple[List[str], List[str]]:
               - 긍정 키워드 리스트 (최대 5개)
               - 부정 키워드 리스트 (최대 5개)
       """
    df = pd.DataFrame(analyzed_data)

    # 감정 필터링
    positive_df = df[df["label"] == "positive"].copy()
    negative_df = df[df["label"] == "negative"].copy()

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

    print(" 긍정 키워드:", pos_list)
    print(" 부정 키워드:", neg_list)

    return pos_list, neg_list
