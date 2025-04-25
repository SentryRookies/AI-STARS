# batch/analyzer/sentiment_batch.py
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from kiwipiepy import Kiwi
import pandas as pd
import re
import os
from typing import List

# 경로 수정
model_dir = r"C:\Users\dkswo\workspace\Project\Sentry\AI\results\0424_model_epoch10_es2_lr2e-5_86"
tokenizer_dir = r"C:\Users\dkswo\.jupyter\sentry\0424_tokenizer_epoch10_es2_lr2e-5_86"

tokenizer = AutoTokenizer.from_pretrained(tokenizer_dir)
model = AutoModelForSequenceClassification.from_pretrained(model_dir)
clf = pipeline("text-classification", model=model, tokenizer=tokenizer)

kiwi = Kiwi()
split_keywords = r"(지만|는데|더라도|고도|하긴 하지만|하긴하지만|하긴했지만|하긴 했지만|불구하고|그럼에도|반면에|대신에)"

def clean_text(text):
    text = re.sub(r'[^\w\s.,!?ㄱ-ㅎ가-힣]', '', text)
    text = re.sub(r'[ㅋㅎㅠㅜ]{2,}', '', text)
    text = re.sub(r'[~!@#\$%\^&\*\(\)_\+=\[\]{}|\\:;"\'<>,.?/]{2,}', '', text)
    return text.strip()

# 문장 분리
def split_sentences(text: str) -> List[str]:
    sentences = kiwi.split_into_sents(text)
    return [s.text.strip() for s in sentences]

# 절 단위 분리 + 전처리
def split_clauses(base_sentence: str) -> List[str]:
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

# 감정 예측 파이프라인 호출
def classify_clause(clause: str) -> dict:
    pred = clf(clause)[0]
    return {
        'text': clause,
        'label': pred['label'],
        'score': round(pred['score'], 4)
    }

def analyze_reviews(reviews: List[dict], save_path: str = None) -> pd.DataFrame:
    results = []

    for item in reviews:  
        text = item.get("content", "")
        for sentence in split_sentences(text):  
            clauses = split_clauses(sentence)
            for clause in clauses:
                result = classify_clause(clause)
                results.append(result)

    df = pd.DataFrame(results)

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        df.to_csv(save_path, index=False, encoding='utf-8-sig')
        print(f"✅ 감정 분석 결과 저장 완료: {save_path}")

    return df