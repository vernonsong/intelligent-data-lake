"""
Mock 服务 API - 提供预置数据
"""
from fastapi import APIRouter, HTTPException
from app.services import mock_data

router = APIRouter()


@router.get("/meta/tables/{db}/{schema}/{table}")
def get_table_info(db: str, schema: str, table: str):
    """获取表信息"""
    result = mock_data.get_table_info(db, schema, table)
    if not result:
        raise HTTPException(status_code=404, detail="表不存在")
    return result


@router.get("/meta/tables/{db}/{schema}/{table}/columns")
def get_columns(db: str, schema: str, table: str):
    """获取字段信息"""
    result = mock_data.get_columns(db, schema, table)
    if not result:
        raise HTTPException(status_code=404, detail="表不存在")
    return result


@router.get("/integration/tasks/by-table/{table}")
def get_task_by_table(table: str):
    """根据表查询任务"""
    result = mock_data.get_task_by_table(table)
    if not result:
        raise HTTPException(status_code=404, detail="任务不存在")
    return result


@router.get("/integration/tasks/{task_id}")
def get_task(task_id: str):
    """获取任务详情"""
    result = mock_data.get_task(task_id)
    if not result:
        raise HTTPException(status_code=404, detail="任务不存在")
    return result


@router.get("/scheduler/schedules/by-task/{task_id}")
def get_schedule_by_task(task_id: str):
    """根据任务获取调度"""
    result = mock_data.get_schedule_by_task(task_id)
    if not result:
        raise HTTPException(status_code=404, detail="调度不存在")
    return result


@router.get("/scheduler/schedules/{schedule_id}")
def get_schedule(schedule_id: str):
    """获取调度详情"""
    result = mock_data.get_schedule(schedule_id)
    if not result:
        raise HTTPException(status_code=404, detail="调度不存在")
    return result


@router.put("/scheduler/schedules/{schedule_id}")
def update_schedule(schedule_id: str, cron_expression: str, description: str):
    """更新调度"""
    success = mock_data.update_schedule(schedule_id, cron_expression, description)
    if not success:
        raise HTTPException(status_code=404, detail="调度不存在")
    return {"status": "success", "message": "调度更新成功"}


@router.get("/scheduler/schedules/{schedule_id}/verify")
def verify_schedule(schedule_id: str):
    """验证调度运行"""
    return mock_data.verify_schedule(schedule_id)
