import os
from dotenv import load_dotenv

load_dotenv()

class OpenRouterConfig:
    API_KEY = os.getenv("OPENROUTER_API_KEY")
    BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")
    HEADERS = {
        "Authorization": f"Bearer {API_KEY}",
        "HTTP-Referer": "https://portfolio.beddinao.me",
        "X-Title": "Agentic Q&A System"
    }
