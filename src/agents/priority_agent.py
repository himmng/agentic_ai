def priority_agent(sentiment, csat):
    if sentiment == "negative" and csat <= 3:
        return True, "high"
    return False, "normal"
