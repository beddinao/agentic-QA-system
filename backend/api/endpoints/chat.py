from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from models.chat import ChatRequest, ChatResponse
from agents.qa_agent import QAAgent
from supabase import create_client
import os
import uuid
import json

#almost
router = APIRouter(prefix="/chat")
agent = QAAgent()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY"))

@router.post("/")
async def chat_endpoint(request: ChatRequest):
    print(f"--- [CHAT]: got request: {request.message}, history: {request.history}")

    if not request.conversation_id:
        conversation_result = supabase.table("conversations").insert({
            "title": request.message[:50]
        }).execute()
        conversation_id = conversation_result.data[0]["id"]
        print(f"--- [CHAT]: creating new conversation: {conversation_id}")
    else:
        conversation_id = request.conversation_id

    supabase.table("message").insert({
        "conversation_id": conversation_id,
        "role": "user",
        "content": request.message
    }).execute()

    result = agent.generate_response(request.message, request.history)

    print(f"--- [CHAT]: got ai response: {result['content']}")

    supabase.table("message").insert({
        "conversation_id": conversation_id,
        "role": "assistant",
        "content": result["content"],
        "citations": result["citations"]
    }).execute()

    return {
        "content": result["content"],
        "citations": result["citations"],
        "conversation_id": conversation_id
    }

@router.post("/stream")
async def chat_stream(request: ChatRequest):
    async def generate():
        result = agent.generate_response(request.message, request.history)
        yield f"data: {json.dumps(result)}\n\n"

    return StreamingResponse(generate(), media_type="text/plain")
