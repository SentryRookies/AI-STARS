from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import pandas as pd
from kiwipiepy import Kiwi
import re

# ✅ 저장된 모델 경로
model_dir = r"C:\Users\dkswo\workspace\Project\Sentry\AI\results\0424_model_epoch10_es2_lr2e-5_86"
tokenizer_dir = r"C:\Users\dkswo\.jupyter\sentry\0424_tokenizer_epoch10_es2_lr2e-5_86"

# ✅ 모델 및 토크나이저 로드
tokenizer = AutoTokenizer.from_pretrained(tokenizer_dir)
model = AutoModelForSequenceClassification.from_pretrained(model_dir)

# ✅ 추론용 파이프라인 생성
sentiment_analyzer = pipeline("text-classification", model=model, tokenizer=tokenizer)

# ✅ 리뷰 파일 불러오기
df = pd.read_excel(r"C:\Users\dkswo\workspace\Project\Sentry\AI\SeoulLandReviews.xlsx")  # 컬럼명 'content'로 가정

# ✅ Kiwi 문장 분석기
kiwi = Kiwi()

# ✅ 전환 접속어 기준 절 나누기
split_keywords = r"(지만|는데|더라도|고도|하긴 하지만|하긴하지만|하긴했지만|하긴 했지만|불구하고|그럼에도|반면에|대신에)"

# ✅ 특수기호 제거 함수
def clean_text(text):
    text = re.sub(r'[^\w\s.,!?ㄱ-ㅎ가-힣]', '', text)
    text = re.sub(r'[ㅋㅎㅠㅜ]{2,}', '', text)
    text = re.sub(r'[~!@#\$%\^&\*\(\)_\+=\[\]{}|\\:;"\'<>,.?/]{2,}', '', text)
    return text.strip()

results = []

# ✅ 최대 100개 리뷰에 대해 분석
for idx in range(min(100, len(df))):
    text = df['content'][idx]
    sentences = kiwi.split_into_sents(text)

    for s in sentences:
        base = s.text.strip()
        sub_clauses = re.split(split_keywords, base)

        full_clauses = []
        for j in range(0, len(sub_clauses), 2):
            clause = sub_clauses[j].strip()
            if j + 1 < len(sub_clauses):
                clause += sub_clauses[j + 1]
            if clause:
                cleaned = clean_text(clause)
                if cleaned:
                    full_clauses.append(cleaned)

        for c in full_clauses:
            preds = sentiment_analyzer(c)
            label = preds[0]['label']
            score = preds[0]['score']
            results.append({
                'text': c,
                'label': label,
                'score': round(score, 4)
            })

# ✅ 결과 저장
result_df = pd.DataFrame(results)
save_path = r"C:\Users\dkswo\workspace\Project\Sentry\AI\SeoulLandReviewspnn.xlsx"
result_df.to_csv(save_path, index=False, encoding='utf-8')
print("✅ CSV 저장 완료:", save_path)
