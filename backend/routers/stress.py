import os
import json
import re
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter()

class ChatMessage(BaseModel):
    role: str
    text: str

class Request(BaseModel):
    device_id: str
    history: List[ChatMessage]
    current_message: str

class Response(BaseModel):
    has_stress: bool
    category_tag: str
    empathy_message: str
    search_keywords: List[str]

SYSTEM_PROMPT = """You are ArameshYar (آرامشیار), a professional Persian mental health AI.
Analyze user input + history. Detect language (fa/en/mixed). Respond in user's language.
Categories: anxiety, depression, anger, sleep, burnout, exam_stress, joy.
ALWAYS end with an open-ended question.
JSON only:
{"has_stress": bool, "category_tag": str, "empathy_message": str, "search_keywords": [str]}"""

async def call_deepseek(messages: list) -> dict:
    """DeepSeek API - Cheap, good Persian"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return None
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(
                "https://api.deepseek.com/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "deepseek-chat",
                    "messages": messages,
                    "temperature": 0.3,
                    "max_tokens": 800,
                    "response_format": {"type": "json_object"}
                }
            )
            if r.status_code == 200:
                content = r.json()["choices"][0]["message"]["content"]
                match = re.search(r'\{.*\}', content, re.DOTALL)
                return json.loads(match.group(0)) if match else json.loads(content)
    except Exception as e:
        print(f"DeepSeek error: {e}")
    return None

async def call_huggingface(messages: list) -> dict:
    """HuggingFace - Free tier but rate limited"""
    hf_token = os.getenv("HF_TOKEN", "")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(
                "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-7B-Instruct/v1/chat/completions",
                headers={"Authorization": f"Bearer {hf_token}"},
                json={
                    "model": "Qwen/Qwen2.5-7B-Instruct",
                    "messages": messages,
                    "temperature": 0.3,
                    "max_tokens": 800,
                    "response_format": {"type": "json_object"}
                }
            )
            if r.status_code == 200:
                content = r.json()["choices"][0]["message"]["content"]
                match = re.search(r'\{.*\}', content, re.DOTALL)
                return json.loads(match.group(0)) if match else json.loads(content)
    except Exception as e:
        print(f"HF error: {e}")
    return None

async def call_ollama(messages: list) -> dict:
    """Local Ollama - FREE, no internet needed on server"""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            prompt = f"{SYSTEM_PROMPT}\n\nConversation:\n"
            for m in messages:
                prompt += f"{'User' if m['role']=='user' else 'AI'}: {m['content']}\n"
            prompt += "AI (JSON):"
            
            r = await client.post("http://localhost:11434/api/generate", json={
                "model": "qwen2.5:7b",
                "prompt": prompt,
                "stream": False,
                "format": "json"
            })
            if r.status_code == 200:
                content = r.json()["response"]
                return json.loads(content)
    except Exception as e:
        print(f"Ollama error: {e}")
    return None

@router.post("/analyze-chat", response_model=Response)
async def analyze_chat(req: Request):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in req.history:
        messages.append({"role": "user" if msg.role=="user" else "assistant", "content": msg.text})
    messages.append({"role": "user", "content": req.current_message})
    
    # Priority: DeepSeek (cheap+reliable) → HuggingFace (free) → Ollama (local)
    result = await call_deepseek(messages)
    if not result:
        result = await call_huggingface(messages)
    if not result:
        result = await call_ollama(messages)
    
    if not result:
        raise HTTPException(status_code=503, detail="All AI providers unavailable")
    
    # Force boolean casting for has_stress
    if "has_stress" in result:
        result["has_stress"] = bool(result["has_stress"])
        
    return Response(**result)
