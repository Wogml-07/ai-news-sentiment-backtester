import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import pandas as pd
import numpy as np

# 2. 감성 스코어링 클래스 정의
class FinancialSentimentScorer:
    def __init__(self, model_name="snunlp/KR-FinBERT-SC"):
        print(f"[{model_name}] 모델 및 토크나이저 다운로드 중... (약 1~2분 소요)")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)

        # 코랩의 GPU(CUDA) 할당 여부 확인
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()
        print(f"👍 모델 로드 완료! 연동된 디바이스: {self.device}")

    def compute_sentiment_score(self, text: str) -> dict:
        """단일 텍스트의 긍정/부정/중립 확률 및 최종 스코어 계산"""
        if not text or not text.strip():
            return {"sentiment_score": 0.0, "dominant_label": "neutral", "prob_positive": 0.0, "prob_negative": 0.0, "prob_neutral": 1.0}

        # 텍스트 토큰화 및 디바이스 전송
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True
        ).to(self.device)

        # 모델 추론 (기울기 계산 비활성화로 메모리 절약)
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probabilities = F.softmax(logits, dim=-1).squeeze().cpu().numpy()

        # KR-FinBERT-SC 레이블 매핑 (0: 부정, 1: 중립, 2: 긍정)
        prob_neg = float(probabilities[0])
        prob_neu = float(probabilities[1])
        prob_pos = float(probabilities[2])

        # 가중치 감성 스코어 공식 적용 (-1.0 ~ +1.0)
        sentiment_score = prob_pos - prob_neg

        # 가장 확률이 높은 대표 레이블 추출
        max_idx = np.argmax(probabilities)
        labels = ["negative", "neutral", "positive"]
        final_label = labels[max_idx]

        return {
            "sentiment_score": round(sentiment_score, 4),
            "dominant_label": final_label,
            "prob_positive": round(prob_pos, 4),
            "prob_negative": round(prob_neg, 4),
            "prob_neutral": round(prob_neu, 4)
        }

    def pipeline_scoring(self, df: pd.DataFrame, text_column: str) -> pd.DataFrame:
        """데이터프레임 내 크롤링 텍스트 일괄 스코어링"""
        print(f"\n🚀 총 {len(df)}건의 크롤링 데이터 분석을 시작합니다.")

        scores, labels, pos_probs, neg_probs, neu_probs = [], [], [], [], []

        for idx, row in df.iterrows():
            text = str(row[text_column])
            res = self.compute_sentiment_score(text)

            scores.append(res["sentiment_score"])
            labels.append(res["dominant_label"])
            pos_probs.append(res["prob_positive"])
            neg_probs.append(res["prob_negative"])
            neu_probs.append(res["prob_neutral"])

        # 데이터프레임에 결과 컬럼 추가
        df["sentiment_score"] = scores
        df["sentiment_label"] = labels
        df["prob_positive"] = pos_probs
        df["prob_negative"] = neg_probs
        df["prob_neutral"] = neu_probs

        print("✅ 모든 데이터 분석이 완료되었습니다.")
        return df

# ==========================================
# 3. 실전 테스트 실행
# ==========================================
if __name__ == "__main__":
    # 스코어러 객체 생성 (최초 실행 시 모델 다운로드 진행)
    scorer = FinancialSentimentScorer()

    # 크롤링한 뉴스라고 가정된 샘플 데이터셋 생성
    crawled_news = {
        "date": ["2026-05-26", "2026-05-27", "2026-05-28", "2026-05-28"],
        "headline": [
            "삼성전자, 차세대 AI 반도체 독점 공급 계약 체결... 주가 시간외 상한가",
            "글로벌 인플레이션 우려 재점화, 금리 인상 가능성에 코스피 2% 급락",
            "현대차, 신형 전기차 출시회 개최... 시장 반응은 예상 수준에 머물러",
            "정부, 바이오 산업 육성을 위한 대규모 예산 편성 정책 발표"
        ]
    }
    df_crawled = pd.DataFrame(crawled_news)

    # 알고리즘 파이프라인 구동 ('headline' 컬럼 기준 분석)
    df_final = scorer.pipeline_scoring(df_crawled, text_column="headline")

    # 코랩에서 보기 좋게 렌더링하기 위해 판다스 출력 설정 변경
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)

    # 결과 출력
    print("\n[최종 감성 분석 결과 데이터프레임]")
    display(df_final)  # 코랩 환경용 데이터프레임 시각화 함수
