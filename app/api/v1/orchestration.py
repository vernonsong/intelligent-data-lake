from fastapi import APIRouter

router = APIRouter()

@router.post("/create")
async def create_scenario():
    """创建新场景 - SSE"""
    pass

@router.get("/tasks/{task_id}")
async def get_task(task_id: str):
    """获取任务状态"""
    pass
