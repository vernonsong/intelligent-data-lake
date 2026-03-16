"""Mock 数据服务 - 预置数据"""

from typing import Dict, List, Optional

class MetaCenterMock:
    """元数据中心 Mock"""
    
    def __init__(self):
        self.tables = {
            "aaa.bbb.ccc": {
                "db": "aaa",
                "schema": "bbb",
                "table": "ccc",
                "columns": [
                    {"name": "id", "type": "BIGINT", "nullable": False},
                    {"name": "name", "type": "VARCHAR(100)", "nullable": False},
                    {"name": "value", "type": "DECIMAL(18,2)", "nullable": True},
                    {"name": "created_at", "type": "TIMESTAMP", "nullable": False},
                    {"name": "updated_at", "type": "TIMESTAMP", "nullable": True},
                ],
                "comment": "示例湖表"
            }
        }
    
    def get_table(self, db: str, schema: str, table: str) -> Optional[Dict]:
        key = f"{db}.{schema}.{table}"
        return self.tables.get(key)
    
    def get_columns(self, db: str, schema: str, table: str) -> Optional[List[Dict]]:
        table = self.get_table(db, schema, table)
        return table["columns"] if table else None


class IntegrationMock:
    """集成任务平台 Mock"""
    
    def __init__(self):
        self.tasks = {
            "task_001": {
                "task_id": "task_001",
                "task_name": "aaa_bbb_ccc_integration",
                "source_table": "aaa.source.source_table",
                "target_table": "aaa.bbb.ccc",
                "schedule_id": "schedule_001",
                "status": "running",
                "mappings": [
                    {"source": "id", "target": "id"},
                    {"source": "name", "target": "name"},
                    {"source": "value", "target": "value"},
                    {"source": "created_time", "target": "created_at"},
                    {"source": "modified_time", "target": "updated_at"},
                ]
            }
        }
    
    def get_tasks_by_table(self, table: str) -> List[Dict]:
        return [t for t in self.tasks.values() if t["target_table"] == table]
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        return self.tasks.get(task_id)


class SchedulerMock:
    """调度任务平台 Mock"""
    
    def __init__(self):
        self.schedules = {
            "schedule_001": {
                "schedule_id": "schedule_001",
                "task_id": "task_001",
                "task_name": "aaa_bbb_ccc_integration",
                "cron_expression": "0 */30 * * *",
                "cron_description": "每 30 分钟执行一次",
                "enabled": True,
                "status": "active"
            }
        }
    
    def get_schedule_by_task(self, task_id: str) -> Optional[Dict]:
        for sched in self.schedules.values():
            if sched["task_id"] == task_id:
                return sched
        return None
    
    def update_schedule(self, schedule_id: str, updates: Dict) -> Dict:
        if schedule_id not in self.schedules:
            return {"success": False, "error": "调度不存在"}
        old = self.schedules[schedule_id].copy()
        self.schedules[schedule_id].update(updates)
        return {"success": True, "old_config": old, "new_config": self.schedules[schedule_id]}
    
    def verify_running(self, schedule_id: str) -> bool:
        sched = self.schedules.get(schedule_id)
        return sched and sched.get("enabled") and sched.get("status") == "active"


# 单例实例
meta_center = MetaCenterMock()
integration = IntegrationMock()
scheduler = SchedulerMock()
