from transformers import BertTokenizer, AutoModelForSequenceClassification, pipeline
from kiwipiepy import Kiwi
import pandas as pd
import re
import os
from typing import List

# 모델 경로dd
# modelDir = r"C:\Users\user\workspace\Sentry\AI-STARS\AiService\model\0424_model_epoch10_es2_lr2e-5_86"
# tokenizerDir = r"C:\Users\user\workspace\Sentry\AI-STARS\AiService\model\0424_tokenizer_epoch10_es2_lr2e-5_86"
baseDir = os.path.dirname(__file__)
tokenizerDir = os.path.abspath(os.path.join(baseDir, "../model/0424_tokenizer_epoch10_es2_lr2e-5_86/0424_tokenizer_epoch10_es2_lr2e-5_86"))
modelDir = os.path.abspath(os.path.join(baseDir, "../model/0424_model_epoch10_es2_lr2e-5_86/0424_model_epoch10_es2_lr2e-5_86"))

tokenizer = BertTokenizer.from_pretrained(tokenizerDir, local_files_only=True)
#tokenizer = BertTokenizer(vocab_file=os.path.join(tokenizerDir, "vocab.txt"))
model = AutoModelForSequenceClassification.from_pretrained(modelDir, local_files_only=True)
clf = pipeline("text-classification", model=model, tokenizer=tokenizer)

kiwi = Kiwi()
splitKeywords = r"(지만|는데|더라도|고도|하긴 하지만|하긴하지만|하긴했지만|하긴 했지만|불구하고|그럼에도|반면에|대신에)"

def cleanText(text):
    text = re.sub(r'[^\w\s.,!?ㄱ-ㅎ가-힣]', '', text)
    text = re.sub(r'[ㅋㅎㅠㅜ]{2,}', '', text)
    text = re.sub(r'[~!@#\$%\^&\*\(\)_\+=\[\]{}|\\:;"\'<>,.?/]{2,}', '', text)
    return text.strip()

def splitSentences(text: str) -> List[str]:
    sentences = kiwi.split_into_sents(text)
    return [s.text.strip() for s in sentences]

def splitClauses(baseSentence: str) -> List[str]:
    subClauses = re.split(splitKeywords, baseSentence)
    clauses = []
    for j in range(0, len(subClauses), 2):
        clause = subClauses[j].strip()
        if j + 1 < len(subClauses):
            clause += subClauses[j + 1]
        cleaned = cleanText(clause)
        if cleaned:
            clauses.append(cleaned)
    return clauses

def classifyClause(clause: str) -> dict:
    if not clause.strip():
        return None  # 빈 문장은 무시

    pred = clf(clause)[0]
    return {
        "text": clause,
        "label": pred["label"],
        "score": round(pred["score"], 4)
    }
def analyzeReviews(reviews: List[dict], savePath: str = None) -> List[dict]:
    results = []

    for item in reviews:
        text = item.get("content", "")
        for sentence in splitSentences(text):
            clauses = splitClauses(sentence)
            for clause in clauses:
                result = classifyClause(clause)
                if result:  # None 아닌 경우만 추가
                    results.append(result)


    # ✅ 키 검증 추가
    validated_results = []
    for r in results:
        if all(k in r for k in ("text", "label", "score")):
            validated_results.append(r)
    print(f"검증된 결과 개수: {len(validated_results)}")

    if savePath:
        os.makedirs(os.path.dirname(savePath), exist_ok=True)
        df = pd.DataFrame(validated_results)   
        df.to_csv(savePath, index=False, encoding='utf-8-sig')
        print(f"✅ 감정 분석 결과 저장 완료: {savePath}")

    return validated_results  

