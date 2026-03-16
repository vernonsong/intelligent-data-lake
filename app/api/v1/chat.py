"""
聊天 API - SSE 流式响应（真实大模型）
"""
import asyncio
import json
from typing import AsyncGenerator
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import httpx

router = APIRouter()

# 阿里云百炼 API 配置 - 从环境变量获取
import os
API_KEY = os.getenv("DASHSCOPE_API_KEY", "sk-sp-0aa99843838b46729778fac5b6ff5e30")
API_URL = os.getenv("DASHSCOPE_API_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions")
MODEL = os.getenv("DASHSCOPE_MODEL", "qwen3.5-plus")


class ChatMessage(BaseModel):
    session_id: str
    message: str
    user_id: str = "user_001"


async def call_llm(messages: list) -> str:
    """调用大模型 API"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "max_tokens": 500
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]


async def generate_response(message: str) -> AsyncGenerator[str, None]:
    """生成 SSE 流式响应 - 真实大模型调用"""
    
    # 步骤 1: 意图识别（调用大模型）
    yield f'event: progress\ndata: {{"step": "意图识别", "status": "running"}}\n\n'
    
    system_prompt = """你是智能入湖系统的意图识别助手。
支持以下场景：
1. 修改调度时间 - 用户说"修改调度"、"变更调度时间"等
2. 新增湖表 - 用户说"新增表"、"创建湖表"等
3. 新增字段 - 用户说"新增字段"、"添加列"等
4. 查询信息 - 用户说"查询"、"查看"等
5. 其他 - 无法识别的意图

只返回 JSON 格式：{"intent": "场景类型", "confidence": 0.95}
"""
    
    try:
        llm_response = await call_llm([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ])
        
        # 解析意图
        intent_data = json.loads(llm_response.strip())
        intent = intent_data.get("intent", "unknown")
        confidence = intent_data.get("confidence", 0.5)
        
        yield f'event: progress\ndata: {{"step": "意图识别", "status": "done", "intent": "{intent}", "confidence": {confidence}}}\n\n'
        
        # 步骤 2: 根据意图回复（调用大模型）
        reply_prompt = f"""根据用户意图 '{intent}'，回复用户。
要求：
- 简洁友好
- 如果是修改调度，询问具体表信息
- 如果是新增表，询问表名和字段
- 如果是查询，询问具体查询内容

用户消息：{message}
"""
        
        reply = await call_llm([
            {"role": "system", "content": "你是智能入湖助手，友好专业。"},
            {"role": "user", "content": reply_prompt}
        ])
        
        yield f'event: message\ndata: {{"role": "assistant", "content": "{reply}"}}\n\n'
        yield f'event: complete\ndata: {{"session_id": "session_{asyncio.get_event_loop().time()}"}}\n\n'
        
    except Exception as e:
        yield f'event: error\ndata: {{"error": "{str(e)}"}}\n\n'


@router.post("/message")
async def send_message(chat_msg: ChatMessage):
    """发送消息 - SSE 流式响应（真实大模型）"""
    return StreamingResponse(
        generate_response(chat_msg.message),
        media_type="text/event-stream"
    )


@router.get("/sessions")
async def list_sessions():
    """获取会话列表"""
    return {
        "sessions": [
            {"id": "session_001", "created_at": "2026-03-16T00:00:00Z", "last_message": "修改调度时间"}
        ]
    }


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """获取会话详情"""
    return {
        "id": session_id,
        "messages": [
            {"role": "user", "content": "修改调度时间", "timestamp": "2026-03-16T00:00:00Z"},
            {"role": "assistant", "content": "您好，请问具体修改哪个表的调度时间？", "timestamp": "2026-03-16T00:00:01Z"}
        ]
    }
