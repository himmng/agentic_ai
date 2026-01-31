def recommendation_agent(sentiment):
    if sentiment == "negative":
        return [
            "Investigate issue",
            "Contact customer proactively"
        ]
    return ["No action required"]
