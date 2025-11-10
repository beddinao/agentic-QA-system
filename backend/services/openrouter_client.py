import os
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from configs.openrouter import OpenRouterConfig


def create_openrouter_llm():
    return ChatOpenAI(
        model=OpenRouterConfig.MODEL,
        api_key=OpenRouterConfig.API_KEY,
        base_url=OpenRouterConfig.BASE_URL,
        default_headers=OpenRouterConfig.HEADERS,
        temperature=0,
        streaming=True,
        stream_usage=True
    )

def get_user_name():
    """prints a string to the console"""

    print("HELLO I HAVE BEEN CALLED")

    return "BEDDINAO"

def test_openrouter_configurations():
    print("--- [OPENROUTER]: testing connection..")
    try:
        prompt = """
        You are a Personal Assitant, your job is to assist your users in any way possible.

        *** IMPORTANT RULE: ***
        1. always use the get_user_name tool to know the user's name before answering any questions.
        2. always mention your sources, if you got the name then where you got it
        """
        llm = create_openrouter_llm()
        agent = create_agent(
            model=llm,
            tools=[get_user_name],
            system_prompt=prompt
        )

        for token, metadata in agent.stream(
            {"messages": [{"role": "user", "content": "what is my name?"}]},
            stream_mode="messages"
        ):
            print(f"node: {metadata['langgraph_node']}")
            print(f"content: {token.content_blocks}")
            print("\n")

        return True
    except Exception as e:
        print(f"--- [OPENROUTER]: missconfigured: {str(e)}")
        return False


