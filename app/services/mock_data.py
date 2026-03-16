"""
Mock 数据服务 - 提供预置数据
"""

# 模块级别变量（用于导入）
meta_center = MOCK_TABLES = {
    "aaa.bbb.ccc": {
        "table_name": "ccc",
        "schema_name": "bbb",
        "db_name": "aaa",
        "columns": [
            {"name": "id", "type": "BIGINT", "nullable": False},
            {"name": "name", "type": "VARCHAR(100)", "nullable": True},
            {"name": "created_at", "type": "TIMESTAMP", "nullable": False},
            {"name": "updated_at", "type": "TIMESTAMP", "nullable": True},
            {"name": "status", "type": "INT", "nullable": True},
        ]
    }
}

# 集成任务 Mock 数据
integration = MOCK_TASKS = {
    "task_001": {
        "task_id": "task_001",
        "table": "aaa.bbb.ccc",
        "status": "running",
        "field_mappings": []
    }
}

# 调度配置 Mock 数据
scheduler = MOCK_SCHEDULES = {
    "schedule_001": {
        "schedule_id": "schedule_001",
        "task_id": "task_001",
        "cron_expression": "0 */30 * * *",
        "description": "每 30 分钟执行",
        "status": "active"
    }
}


def get_table_info(db: str, schema: str, table: str):
    """获取表信息"""
    key = f"{db}.{schema}.{table}"
    return MOCK_TABLES.get(key)


def get_columns(db: str, schema: str, table: str):
    """获取字段信息"""
    table_info = get_table_info(db, schema, table)
    if table_info:
        return table_info["columns"]
    return None


def get_task_by_table(table: str):
    """根据表查询任务"""
    for task in MOCK_TASKS.values():
        if task["table"] == table:
            return task
    return None


def get_task(task_id: str):
    """获取任务详情"""
    return MOCK_TASKS.get(task_id)


def get_schedule_by_task(task_id: str):
    """根据任务获取调度"""
    for schedule in MOCK_SCHEDULES.values():
        if schedule["task_id"] == task_id:
            return schedule
    return None


def get_schedule(schedule_id: str):
    """获取调度详情"""
    return MOCK_SCHEDULES.get(schedule_id)


def update_schedule(schedule_id: str, cron_expression: str, description: str):
    """更新调度"""
    if schedule_id in MOCK_SCHEDULES:
        MOCK_SCHEDULES[schedule_id]["cron_expression"] = cron_expression
        MOCK_SCHEDULES[schedule_id]["description"] = description
        return True
    return False


def verify_schedule(schedule_id: str):
    """验证调度运行"""
    schedule = get_schedule(schedule_id)
    if schedule:
        return {"valid": True, "message": "调度验证通过", "next_run": "2026-03-15 23:30:00"}
    return {"valid": False, "message": "调度不存在"}
