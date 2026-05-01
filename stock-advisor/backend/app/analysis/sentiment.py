"""Sentiment analysis: news sentiment scoring (placeholder for now).

Will use simple keyword-based sentiment for Chinese financial text.
Future: integrate with LLM or dedicated sentiment API.
"""

# Positive keywords in Chinese financial context
POSITIVE_WORDS = [
    "增长", "盈利", "突破", "利好", "回购", "增持", "分红",
    "中标", "签约", "获批", "创新高", "超预期", "扭亏",
]

# Negative keywords
NEGATIVE_WORDS = [
    "亏损", "减持", "暴雷", "退市", "违规", "处罚", "诉讼",
    "下滑", "暴跌", "跌停", "减值", "商誉", "债务",
]


def analyze_sentiment(text: str) -> float:
    """
    Simple keyword-based sentiment analysis.
    Returns float between -1 (negative) and 1 (positive).
    """
    if not text:
        return 0.0

    pos_count = sum(1 for w in POSITIVE_WORDS if w in text)
    neg_count = sum(1 for w in NEGATIVE_WORDS if w in text)

    total = pos_count + neg_count
    if total == 0:
        return 0.0

    return (pos_count - neg_count) / total
