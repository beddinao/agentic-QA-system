import os
from langchain_openai import ChatOpenAI
from configs.openrouter import OpenRouterConfig


def create_openrouter_llm():
    return ChatOpenAI(
        model=OpenRouterConfig.MODEL,
        api_key=OpenRouterConfig.API_KEY,
        base_url=OpenRouterConfig.BASE_URL,
        default_headers=OpenRouterConfig.HEADERS,
        temperature=0,
        streaming=True
    )

def test_openrouter_configurations():
    print("--- [OPENROUTER]: testing connection..")
    try:
        llm = create_openrouter_llm()
        response = llm.invoke("responde like a human. are you alive?")
        print(f"--- [OPENROUTER]: {response.content}")
        return True
    except Exception as e:
        print(f"--- [OPENROUTER]: missconfigured: {str(e)}")
        return False
