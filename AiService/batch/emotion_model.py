from transformers import BertTokenizer, AutoModelForSequenceClassification, pipeline
from kiwipiepy import Kiwi
import pandas as pd
import re
import os
from typing import List

# 모델 경로
base_dir = os.path.dirname(__file__)
tokenizer_dir = os.path.abspath(os.path.join(base_dir, "../model/0424_tokenizer_epoch10_es2_lr2e-5_86/0424_tokenizer_epoch10_es2_lr2e-5_86"))
model_dir = os.path.abspath(os.path.join(base_dir, "../model/0424_model_epoch10_es2_lr2e-5_86/0424_model_epoch10_es2_lr2e-5_86"))

# 감정 분류 파이프라인 정의
tokenizer = BertTokenizer.from_pretrained(tokenizer_dir, local_files_only=True)
model = AutoModelForSequenceClassification.from_pretrained(model_dir, local_files_only=True)
clf = pipeline("text-classification", model=model, tokenizer=tokenizer)

# 문장 분리기
kiwi = Kiwi()

# 전환 접속어 패턴
split_keywords = r"(지만|는데|더라도|고도|하긴 하지만|하긴하지만|하긴했지만|하긴 했지만|불구하고|그럼에도|반면에|대신에)"

label_map = {
    "LABEL_0": "negative",   # 부정
    "LABEL_1": "neutral",    # 중립
    "LABEL_2": "positive"    # 긍정
}

def clean_text(text: str) -> str:
    """
    주어진 텍스트에서 불필요한 요소들을 제거하여 정제된 형태로 반환

    정제 방식:
    - 이모지, 특수문자, 기호를 제거. (한글, 숫자, 일반 구두점 등은 유지)
    - 'ㅋ', 'ㅎ', 'ㅠ', 'ㅜ' 등의 반복되는 감정 표현 문자를 제거
    - 반복되는 특수문자 시퀀스를 제거
    - 최종적으로 앞뒤 공백을 제거

    Args:
        text (str): 정제할 원본 텍스트

    Returns:
        str: 정제된 텍스트
    """
    text = re.sub(r'[^\w\s.,!?ㄱ-ㅎ가-힣]', '', text)
    text = re.sub(r'[ㅋㅎㅠㅜ]{2,}', '', text)
    text = re.sub(r'[~!@#\$%\^&\*\(\)_\+=\[\]{}|\\:;"\'<>,.?/]{2,}', '', text)
    return text.strip()

def split_sentences(text: str) -> List[str]:
    """
    입력된 리뷰 텍스트를 문장 단위로 분리

    Args:
        text (str): 문장 분리를 수행할 전체 리뷰 텍스트

    Returns:
        List[str]: 분리된 문장 문자열들의 리스트 (앞 뒤 공백 제거됨)
    """
    sentences = kiwi.split_into_sents(text)
    return [s.text.strip() for s in sentences]

def split_clauses(base_sentence: str) -> List[str]:
    """
    - 주어진 문장을 여러 절로 나누고, 각 절을 정제하여 리스트로 반환
    - 절은 `split_keywords`로 정의된 키워드를 기준으로 나누며, 각 절은 `clean_text` 함수를 통해 정제됨

    Args:
        base_sentence (str): 절로 나눌 원본 문장

    Returns:
        List[str]: 정제된 절들의 리스트
    """
    sub_clauses = re.split(split_keywords, base_sentence)
    clauses = []
    for j in range(0, len(sub_clauses), 2):
        clause = sub_clauses[j].strip()
        if j + 1 < len(sub_clauses):
            clause += sub_clauses[j + 1]
        cleaned = clean_text(clause)
        if cleaned:
            clauses.append(cleaned)
    return clauses

def classify_clause(clause: str) -> dict:
    """
    주어진 절에 대한 감정 분석을 수행하고 결과 반환

    이 함수는 주어진 절을 감정 분류 모델에 입력하여 해당 절의 감정 레이블과 신뢰도를 반환
    모델 예측 결과를 기반으로, 레이블이 `label_map`에서 정의된 감정으로 매핑됨
    예측된 감정의 신뢰도는 소수점 4자리로 반올림하여 반환

    Args:
        clause (str): 감정 분류할 절

    Returns:
        dict: 감정 분석 결과를 담은 딕셔너리로, 포함된 키는 'text', 'label', 'score'이다.
            - 'text': 입력된 절,
            - 'label': 감정 레이블(긍정: 2, 중립: 1, 부정: 0),
            - 'score': 해당 감정의 신뢰도(0.0 ~ 1.0)
        입력된 절이 비어 있거나 공백만 있을 경우 `None` 반환
    """
    if not clause.strip():
        return None

    pred = clf(clause)[0]
    label = label_map.get(pred["label"], "neutral")  # 기본은 neutral로
    return {
        "text": clause,
        "label": label,
        "score": round(pred["score"], 4)
    }

def analyze_reviews(reviews: List[dict], save_path: str = None) -> List[dict]:
    """
    여러 리뷰를 절 단위로 분해하고, 각 절에 대해 감정 분석을 수행

    이 함수는 입력된 리뷰 리스트에서 텍스트 내용을 추출한 뒤,
    문장 분리(`split_sentences`) → 절 분리(`split_clauses`) → 감정 분류(`classify_clause`)를 거쳐,
    각 절에 대해 감정 결과(`text`, `label`, `score`)를 생성함.
    결과는 유효성 검증 후, 옵션에 따라 CSV 파일로 저장

    Args:
        reviews (List[dict]): 감정 분석 대상 리뷰 리스트.
                              각 리뷰는 'content' 키를 포함한 딕셔너리여야 함.
        save_path (str, optional): 분석 결과를 저장할 CSV 파일 경로.

    Returns:
        List[dict]: 분석된 감정 결과 리스트.
                    각 항목은 다음의 키를 포함
                        - 'text': 절 텍스트
                        - 'label': 감정 레이블(긍정: 2, 중립: 1, 부정: 0)
                        - 'score': 감정 예측의 신뢰도 (0.0 ~ 1.0)
    """
    results = []

    for item in reviews:
        text = item.get("content", "")
        for sentence in split_sentences(text):
            clauses = split_clauses(sentence)
            for clause in clauses:
                result = classify_clause(clause)
                if result:  # None 아닌 경우만 추가
                    results.append(result)

    # ✅ 키 검증 추가
    validated_results = []
    for r in results:
        if all(k in r for k in ("text", "label", "score")):
            validated_results.append(r)
    print(f"검증된 결과 개수: {len(validated_results)}")

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        df = pd.DataFrame(validated_results)
        df.to_csv(save_path, index=False, encoding='utf-8-sig')
        print(f"✅ 감정 분석 결과 저장 완료: {save_path}")

    return validated_results
