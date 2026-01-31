# agent_tester.py
from dotenv import load_dotenv
from invoke_agents import sentiment_agent_run

# Load environment variables from .env
load_dotenv()

# --- Example comment to test sentiment ---
test_comment = (
    "Overall, my experience has been positive, especially with the reliability of supply. "
    "However, the mobile app feels outdated and slow, making it difficult to quickly check my balance or recent usage. "
    "Improving the app usability would significantly enhance the overall customer experience. I am not okay with the service outages though."
)
test_csat = 3

# --- Run the agent using helper function ---
try:
    sentiment = sentiment_agent_run(test_comment, test_csat)  # Uses env SENTIMENT_AGENT_NAME automatically
    print("Sentiment:", sentiment)
except Exception as e:
    print("Error running sentiment agent:", e)
