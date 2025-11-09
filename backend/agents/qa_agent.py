from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate
from services.openrouter_client import create_openrouter_llm
from services.vector_store import vector_store
from langchain.tools import tool
from dotenv import load_dotenv
import os
import json

load_dotenv()

class QAAgent:
    def __init__(self):
        self.llm = create_openrouter_llm()
        self.tools = self._create_tools()
        self.agent = self._create_agent()

    def _create_tools(self):
        @tool
        def document_search(query: str) -> str:
            """Search documentation for relevant and useful informations"""
            print(f"--- [BOT]: document_search tool is being used, query: {query}")

            vector_store_instance = vector_store.get_vector_store()
            docs = vector_store_instance.similarity_search(query, k=3)

            results = []
            for doc in docs:
                print(f"--- [BOT]: found document: {doc.page_content}")
                results.append({
                    "content": doc.page_content,
                    "source": doc.metadata.get("source", "unknown"),
                    "chunk_index": doc.metadata.get("chunk_index", 0)
                })

            return json.dumps(results)
        return [document_search]

    def _create_agent(self):
        system_prompt = """
            You are a very wholesome and helpful documentation assistant for technical documentations. 

            ** IMPORTANT RULES: **
            1. Always use the document_search tool to find information from our database
            2. Always mention your sources, where you found the information
            3. If the documentation doesn't have the answer, say so clearly
            4. Be accurate and try to help as much as possible
            5. Use only simple English words and sentences/syntax
            6. Be as much direct as possible, Always cut to the point
            """

        agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=system_prompt
        )

        return agent

    def generate_response(self, question: str, history: list = None):
        if history is None:
            history = []

        messages = []
        for msg in history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        messages.append({
            "role": "user",
            "content": question
        })

        try:
            result = self.agent.invoke({
                "messages": messages
            })

            final_message = result["messages"][-1]
            answer = final_message.content if hasattr(final_message, 'content') else str(final_message)

            citations = []
            for msg in result.get("messages", []):
                if hasattr(msg, 'type') and msg.type == 'tool':
                    try:
                        search_results = json.loads(msg.content)
                        if isinstance(search_results, list):
                            for doc in search_results:
                                citations.append({
                                    "source": doc.get("source", "unknown"),
                                    "content": doc.get("content", "")[:200] + "...",
                                    "confidence": 0.95
                                })
                    except:
                        pass
            return {
                "content": answer,
                "citations": citations
            }

        except Exception as e:
            return {
                "content": f"I encountered an error: {str(e)}",
                "citations": []
            }

