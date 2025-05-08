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
    """이모티콘/특수기호 제거"""
    # 이모지, 특수문자, 기호 삭제
    text = re.sub(r'[^\w\s.,!?ㄱ-ㅎ가-힣]', '', text)
    # 반복 문자 제거
    text = re.sub(r'[ㅋㅎㅠㅜ]{2,}', '', text)
    # 반복 특수문자 제거
    text = re.sub(r'[~!@#\$%\^&\*\(\)_\+=\[\]{}|\\:;"\'<>,.?/]{2,}', '', text)
    # 앞뒤 공백 제거
    return text.strip()

def split_sentences(text: str) -> List[str]:
    """ 리뷰를 문장 단위로 나누기"""
    sentences = kiwi.split_into_sents(text)
    return [s.text.strip() for s in sentences]

def split_clauses(base_sentence: str) -> List[str]:
    """ 한 문장을 여러 절로 나누기"""
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
    """하나의 절에 대한 감정 분류"""
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
    """하나의 리뷰를 여러 개의 절별 감정 분석 결과로 변환"""
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
