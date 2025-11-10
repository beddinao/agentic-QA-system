from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from models.chat import ChatRequest, ChatResponse, StreamResponse
from agents.qa_agent import QAAgent
from services.vector_store import vector_store
from services.openrouter_client import test_openrouter_configurations
from supabase import create_client
from datetime import datetime
import os
import uuid
import asyncio
import json

#almost
router = APIRouter(prefix="/chat")
agent = QAAgent()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY"))

def _get_current_time():
    try:
        return datetime.now().strftime("%H:%M:%S")
    except Exception:
        return ""

def check_conversation_id(request: ChatRequest):
    if not request.conversation_id:
        conversation_result = supabase.table("conversations").insert({
            "title": request.message[:50]
        }).execute()
        conversation_id = conversation_result.data[0]["id"]
        print(f"--- [CHAT][{_get_current_time()}]: created new conversation: {conversation_id}")
        return conversation_id
    else:
        return request.conversation_id

def store_user_message(request: ChatRequest, conversation_id):
    supabase.table("message").insert({
        "conversation_id": conversation_id,
        "role": "user",
        "content": request.message
    }).execute()

def store_assistant_message(content: str, citations: list, conversation_id: str):
    result = supabase.table("message").insert({
        "conversation_id": conversation_id,
        "role": "assistant",
        "content": content,
        "citations": citations
    }).execute()
    return result.data[0]["id"] if result.data else None


@router.post("/")
async def chat_endpoint(request: ChatRequest):
    print(f"--- [CHAT][{_get_current_time()}]: got request: {request.message}")

    conversation_id = check_conversation_id(request) 
    store_user_message(request, conversation_id)

    result = agent.generate_response(request.message, request.history)
    store_assistant_message(result["content"], result["citations"], conversation_id) 

    print(f"--- [CHAT][{_get_current_time()}]: ai response is ready")

    return {
        "content": result["content"],
        "citations": result["citations"],
        "conversation_id": conversation_id
    }

@router.post("/stream")
async def chat_stream(request: ChatRequest):
    conversation_id = check_conversation_id(request)
    store_user_message(request, conversation_id)

    #test_openrouter_configurations() 

    async def generate():
        try:
            full_content = ""
            citations = []
        
            for chunk in agent.generate_streamed_response(request.message, request.history):
                if chunk['type'] == "response":
                    token = chunk['content']
                    full_content += token
                    stream_data = {
                        "type": "content",
                        "data": {
                            "token": token,
                            "is_final": False
                        }
                    }
                    yield f"data: {json.dumps(stream_data)}\n\n"
                elif chunk['type'] == "citation":
                    citations.append(chunk['content'])
                    citation_data = {
                        "type": "citations",
                        "data": {
                            "citations": chunk['content']
                        }
                    }
                    yield f"data: {json.dumps(citation_data)}\n\n"

            message_id = store_assistant_message(full_content, citations, conversation_id)
            end_data = {
                "type": "end",
                "data": {
                    "conversation_id": conversation_id,
                    "message_id": message_id
                }
            }
            yield f"data: {json.dumps(end_data)}\n\n"
        except Exception as e:
            error_data = {
                "type": "error",
                "data": {
                    "message": str(e)
                }
            }
            yield f"data: {json.dumps(error_data)}\n\n"

    return StreamingResponse(generate(), media_type="text/plain")
