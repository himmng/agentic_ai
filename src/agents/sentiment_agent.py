def sentiment_agent(comment, csat):
    if csat <= 2 or "delayed" in comment.lower():
        return "negative"
    if csat >= 4:
        return "positive"
    return "neutral"
