import os
from dotenv import load_dotenv
from typing import TypedDict, List, Optional
from langchain_openai import AzureChatOpenAI


load_dotenv(".env")

class SentimentState(TypedDict):
    raw_test: str
    cleaned_test: str
    Sentiment: Optional[str]
    confidence: Optional[float]

llm_model = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    temperature=0.0,
)