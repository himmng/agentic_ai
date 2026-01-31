from pseudo_api import get_surveys, write_back_augmented
from agents.sentiment_agent import sentiment_agent
from agents.priority_agent import priority_agent
from agents.summary_agent import summary_agent
from agents.recommendation_agent import recommendation_agent
from agents.escalation_agent import escalation_agent

def run_pipeline(overwrite=False):
    surveys = get_surveys()

    for s in surveys:
        comment = s["answers"]["comment"]
        csat = s["answers"]["csat"]

        sentiment = sentiment_agent(comment, csat)
        s["tags"].append(f"sentiment:{sentiment}")

        incident, priority = priority_agent(sentiment, csat)
        s["case"]["incident"] = incident
        s["case"]["priority"] = priority

        s["case"]["notes"].append(summary_agent(comment))
        s["case"]["notes"].append(
            "AI Actions: " + ", ".join(recommendation_agent(sentiment))
        )

        esc, team, sla = escalation_agent(priority)
        s["workflow"].update({
            "assigned_team": team,
            "sla_hours": sla,
            "escalation": esc
        })

    write_back_augmented(surveys, overwrite=overwrite)
