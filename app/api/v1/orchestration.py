"""
编排 API - 工作流编排和场景创建
"""
import asyncio
import time
import json
from typing import AsyncGenerator, Dict, Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.agents.deepagent import DeepAgent
from app.workflows.workflow import create_modify_schedule_workflow

router = APIRouter()


class CreateScenarioRequest(BaseModel):
    user_request: str
    constraints: list = []
    validation_data: Dict[str, Any] = {}


async def generate_orchestration_response(request: CreateScenarioRequest) -> AsyncGenerator[str, None]:
    """生成编排 SSE 流式响应"""
    
    # 步骤 1: DeepAgents 选取 Skill
    yield f'event: progress\ndata: {{"step": "选取 Skill", "status": "running"}}\n\n'
    
    agent = DeepAgent("orchestration_agent")
    intent = "modify_schedule" if "调度" in request.user_request else "unknown"
    response = await agent.run(request.user_request)
    selected_skills = response.get("skills_needed", [])
    
    await asyncio.sleep(0.5)
    yield f'event: progress\ndata: {{"step": "选取 Skill", "status": "done", "skills": {json.dumps(selected_skills)}}}\n\n'
    
    # 步骤 2: 使用工作流引擎编排
    yield f'event: progress\ndata: {{"step": "编排工作流", "status": "running"}}\n\n'
    await asyncio.sleep(0.5)
    
    # 创建工作流
    workflow = create_modify_schedule_workflow()
    
    if request.validation_data:
        # 执行工作流节点展示
        db = request.validation_data.get("db", "aaa")
        schema = request.validation_data.get("schema", "bbb")
        table = request.validation_data.get("table", "ccc")
        
        yield f'event: workflow_node\ndata: {{"node": "query_table", "status": "completed", "table": "{db}.{schema}.{table}"}}\n\n'
        await asyncio.sleep(0.3)
        
        yield f'event: workflow_node\ndata: {{"node": "check_exists", "status": "completed", "exists": true}}\n\n'
        await asyncio.sleep(0.3)
        
        yield f'event: workflow_node\ndata: {{"node": "query_task", "status": "completed", "count": 1}}\n\n'
        await asyncio.sleep(0.3)
        
        yield f'event: workflow_node\ndata: {{"node": "query_schedule", "status": "completed", "cron": "0 */30 * * *"}}\n\n'
        await asyncio.sleep(0.3)
    
    yield f'event: progress\ndata: {{"step": "编排工作流", "status": "done", "workflow_id": "{workflow.workflow_id}"}}\n\n'
    
    # 步骤 3: 提交验证
    yield f'event: progress\ndata: {{"step": "提交验证", "status": "running"}}\n\n'
    await asyncio.sleep(0.5)
    
    yield f'event: progress\ndata: {{"step": "提交验证", "status": "done"}}\n\n'
    
    # 步骤 4: 完成
    yield f'event: complete\ndata: {{"skill_id": "{workflow.workflow_id}", "status": "pending_confirmation", "agent": "orchestration_agent"}}\n\n'


@router.post("/create")
async def create_scenario(request: CreateScenarioRequest):
    """创建新场景 - SSE 流式响应"""
    return StreamingResponse(
        generate_orchestration_response(request),
        media_type="text/event-stream"
    )


@router.get("/tasks/{task_id}")
async def get_task(task_id: str):
    """获取任务状态"""
    return {
        "task_id": task_id,
        "status": "completed",
        "skill_id": "wf_modify_schedule_v1",
        "progress": 100,
        "agent": "orchestration_agent"
    }


@router.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: str):
    """取消任务"""
    return {"success": True, "message": f"任务 {task_id} 已取消"}
