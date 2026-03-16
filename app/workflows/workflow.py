"""LangGraph 工作流引擎 - 调用真实 Mock 服务 API + 错误处理 + 日志"""

import asyncio
import httpx
import time
import json
from typing import Dict, Any, List, TypedDict, Annotated, Optional
from datetime import datetime

from langgraph.graph import StateGraph, END

from app.core.exceptions import (
    NetworkError, DataError, BusinessError,
    WorkflowError, NotFoundError, IntelligentDataLakeError
)
from app.core.logging_config import get_logger, log_api_call, log_workflow_node


# ==================== 配置 ====================

class WorkflowConfig:
    """工作流配置"""
    MOCK_BASE_URL = "http://localhost:8000/api/v1/mock"
    LOG_LEVEL = "INFO"


# ==================== 工作流状态 ====================

class WorkflowState(TypedDict):
    """工作流状态"""
    input: Dict[str, Any]
    output: Dict[str, Any]
    messages: Annotated[List[str], lambda x, y: x + y]
    context: Dict[str, Any]
    current_node: str
    errors: List[str]
    warnings: List[str]


# ==================== Mock 服务客户端 ====================

class MockServiceClient:
    """Mock 服务 API 客户端 - 增强错误处理和日志"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.logger = get_logger("Workflow.MockClient")
    
    async def get_table(self, db: str, schema: str, table: str) -> Optional[Dict]:
        """查询表信息"""
        url = f"{self.base_url}/meta/tables/{db}/{schema}/{table}"
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                duration_ms = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    log_api_call(self.logger, "GET", url, 200, duration_ms)
                    return response.json()
                elif response.status_code == 404:
                    log_api_call(self.logger, "GET", url, 404, duration_ms, "表不存在")
                    return None
                else:
                    log_api_call(self.logger, "GET", url, response.status_code, duration_ms)
                    return None
        except httpx.TimeoutException:
            duration_ms = (time.time() - start_time) * 1000
            log_api_call(self.logger, "GET", url, 0, duration_ms, "请求超时")
            raise NetworkError(f"查询表信息超时：{db}.{schema}.{table}", url=url)
        except httpx.RequestError as e:
            duration_ms = (time.time() - start_time) * 1000
            log_api_call(self.logger, "GET", url, 0, duration_ms, str(e))
            raise NetworkError(f"查询表信息失败：{str(e)}", url=url)
    
    async def get_tasks_by_table(self, table: str) -> List[Dict]:
        """查询集成任务"""
        url = f"{self.base_url}/integration/tasks/by-table/{table}"
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                duration_ms = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    log_api_call(self.logger, "GET", url, 200, duration_ms)
                    result = response.json()
                    return result.get("tasks", [])
                else:
                    log_api_call(self.logger, "GET", url, response.status_code, duration_ms)
                    return []
        except httpx.TimeoutException:
            duration_ms = (time.time() - start_time) * 1000
            log_api_call(self.logger, "GET", url, 0, duration_ms, "请求超时")
            raise NetworkError(f"查询集成任务超时：{table}", url=url)
        except httpx.RequestError as e:
            duration_ms = (time.time() - start_time) * 1000
            log_api_call(self.logger, "GET", url, 0, duration_ms, str(e))
            raise NetworkError(f"查询集成任务失败：{str(e)}", url=url)
    
    async def get_schedule_by_task(self, task_id: str) -> Optional[Dict]:
        """查询调度配置"""
        url = f"{self.base_url}/scheduler/schedules/by-task/{task_id}"
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                duration_ms = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    log_api_call(self.logger, "GET", url, 200, duration_ms)
                    return response.json()
                elif response.status_code == 404:
                    log_api_call(self.logger, "GET", url, 404, duration_ms, "调度不存在")
                    return None
                else:
                    log_api_call(self.logger, "GET", url, response.status_code, duration_ms)
                    return None
        except httpx.TimeoutException:
            duration_ms = (time.time() - start_time) * 1000
            log_api_call(self.logger, "GET", url, 0, duration_ms, "请求超时")
            raise NetworkError(f"查询调度配置超时：{task_id}", url=url)
        except httpx.RequestError as e:
            duration_ms = (time.time() - start_time) * 1000
            log_api_call(self.logger, "GET", url, 0, duration_ms, str(e))
            raise NetworkError(f"查询调度配置失败：{str(e)}", url=url)
    
    async def update_schedule(self, schedule_id: str, updates: Dict) -> Dict:
        """更新调度"""
        url = f"{self.base_url}/scheduler/schedules/{schedule_id}"
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(url, json=updates, timeout=10.0)
                duration_ms = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    log_api_call(self.logger, "PUT", url, 200, duration_ms)
                    return response.json()
                else:
                    log_api_call(self.logger, "PUT", url, response.status_code, duration_ms)
                    return {"success": False, "error": f"HTTP {response.status_code}"}
        except httpx.TimeoutException:
            duration_ms = (time.time() - start_time) * 1000
            log_api_call(self.logger, "PUT", url, 0, duration_ms, "请求超时")
            raise NetworkError(f"更新调度超时：{schedule_id}", url=url)
        except httpx.RequestError as e:
            duration_ms = (time.time() - start_time) * 1000
            log_api_call(self.logger, "PUT", url, 0, duration_ms, str(e))
            raise NetworkError(f"更新调度失败：{str(e)}", url=url)
    
    async def verify_running(self, schedule_id: str) -> bool:
        """验证运行状态"""
        url = f"{self.base_url}/scheduler/schedules/{schedule_id}/verify"
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                duration_ms = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    log_api_call(self.logger, "GET", url, 200, duration_ms)
                    result = response.json()
                    return result.get("running", False)
                else:
                    log_api_call(self.logger, "GET", url, response.status_code, duration_ms)
                    return False
        except httpx.TimeoutException:
            duration_ms = (time.time() - start_time) * 1000
            log_api_call(self.logger, "GET", url, 0, duration_ms, "请求超时")
            raise NetworkError(f"验证运行状态超时：{schedule_id}", url=url)
        except httpx.RequestError as e:
            duration_ms = (time.time() - start_time) * 1000
            log_api_call(self.logger, "GET", url, 0, duration_ms, str(e))
            raise NetworkError(f"验证运行状态失败：{str(e)}", url=url)


# ==================== 工作流执行器 ====================

class Workflow:
    """工作流执行器 - LangGraph + Mock 服务 API + 错误处理 + 日志"""
    
    def __init__(self, workflow_id: str, name: str):
        self.workflow_id = workflow_id
        self.name = name
        self.mock_client = MockServiceClient(WorkflowConfig.MOCK_BASE_URL)
        self.logger = get_logger(f"Workflow.{workflow_id}")
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """构建 LangGraph"""
        graph = StateGraph(WorkflowState)
        
        # 添加节点
        graph.add_node("query_table", self._query_table_node)
        graph.add_node("check_exists", self._check_exists_node)
        graph.add_node("query_task", self._query_task_node)
        graph.add_node("check_unique", self._check_unique_node)
        graph.add_node("query_schedule", self._query_schedule_node)
        graph.add_node("user_confirm", self._user_confirm_node)
        graph.add_node("update_schedule", self._update_schedule_node)
        graph.add_node("verify_running", self._verify_running_node)
        graph.add_node("end", self._end_node)
        
        # 添加边
        graph.set_entry_point("query_table")
        graph.add_edge("query_table", "check_exists")
        graph.add_edge("check_exists", "query_task")
        graph.add_edge("query_task", "check_unique")
        graph.add_edge("check_unique", "query_schedule")
        graph.add_edge("query_schedule", "user_confirm")
        graph.add_edge("user_confirm", "update_schedule")
        graph.add_edge("update_schedule", "verify_running")
        graph.add_edge("verify_running", "end")
        graph.add_edge("end", END)
        
        return graph.compile()
    
    async def _query_table_node(self, state: WorkflowState) -> WorkflowState:
        """节点 1: 查询表信息 - 调用 Mock 服务 API + 错误处理"""
        db = state["input"].get("db", "aaa")
        schema = state["input"].get("schema", "bbb")
        table = state["input"].get("table", "ccc")
        table_full = f"{db}.{schema}.{table}"
        
        log_workflow_node(self.logger, "query_table", "skill_call", "running", f"查询表：{table_full}")
        
        try:
            table_info = await self.mock_client.get_table(db, schema, table)
            
            if table_info:
                state["context"]["table_info"] = table_info
                state["context"]["exists"] = True
                state["messages"].append(f"表存在：{table_info.get('table')}")
                log_workflow_node(self.logger, "query_table", "skill_call", "success", f"表存在：{table_full}", {"table": table_info})
            else:
                state["context"]["table_info"] = None
                state["context"]["exists"] = False
                state["messages"].append(f"表不存在：{table_full}")
                state["errors"].append(f"表 {table_full} 不存在")
                log_workflow_node(self.logger, "query_table", "skill_call", "warning", f"表不存在：{table_full}")
        except NetworkError as e:
            state["errors"].append(f"网络错误：{e.message}")
            state["context"]["exists"] = False
            log_workflow_node(self.logger, "query_table", "skill_call", "error", f"网络错误：{e.message}", {"url": e.details.get("url")})
        except NotFoundError as e:
            state["errors"].append(f"资源不存在：{e.message}")
            state["context"]["exists"] = False
            log_workflow_node(self.logger, "query_table", "skill_call", "error", f"资源不存在：{e.message}")
        except Exception as e:
            state["errors"].append(f"未知错误：{str(e)}")
            state["context"]["exists"] = False
            log_workflow_node(self.logger, "query_table", "skill_call", "error", f"未知错误：{str(e)}")
        
        state["current_node"] = "query_table"
        return state
    
    async def _check_exists_node(self, state: WorkflowState) -> WorkflowState:
        """节点 2: 检查表存在"""
        exists = state["context"].get("exists", False)
        
        log_workflow_node(self.logger, "check_exists", "condition", "running", f"检查表存在：{exists}")
        
        state["messages"].append(f"检查表存在：{'true' if exists else 'false'}")
        state["context"]["exists"] = exists
        state["current_node"] = "check_exists"
        
        if not exists:
            state["errors"].append("表不存在，无法继续")
            log_workflow_node(self.logger, "check_exists", "condition", "error", "表不存在")
        else:
            log_workflow_node(self.logger, "check_exists", "condition", "success", "表存在检查通过")
        
        return state
    
    async def _query_task_node(self, state: WorkflowState) -> WorkflowState:
        """节点 3: 查询集成任务 - 调用 Mock 服务 API"""
        db = state["input"].get("db", "aaa")
        schema = state["input"].get("schema", "bbb")
        table = state["input"].get("table", "ccc")
        table_full = f"{db}.{schema}.{table}"
        
        log_workflow_node(self.logger, "query_task", "skill_call", "running", f"查询集成任务：{table_full}")
        
        try:
            tasks = await self.mock_client.get_tasks_by_table(table_full)
            
            state["context"]["tasks"] = tasks
            state["context"]["task_count"] = len(tasks)
            state["messages"].append(f"找到 {len(tasks)} 个集成任务")
            
            if tasks:
                state["context"]["task_id"] = tasks[0].get("task_id")
                log_workflow_node(self.logger, "query_task", "skill_call", "success", f"找到{len(tasks)}个任务", {"task_id": tasks[0].get("task_id")})
            else:
                state["warnings"] = state.get("warnings", []) + ["未找到集成任务"]
                log_workflow_node(self.logger, "query_task", "skill_call", "warning", "未找到集成任务")
        except NetworkError as e:
            state["errors"].append(f"网络错误：{e.message}")
            log_workflow_node(self.logger, "query_task", "skill_call", "error", f"网络错误：{e.message}")
        except Exception as e:
            state["errors"].append(f"未知错误：{str(e)}")
            log_workflow_node(self.logger, "query_task", "skill_call", "error", f"未知错误：{str(e)}")
        
        state["current_node"] = "query_task"
        return state
    
    async def _check_unique_node(self, state: WorkflowState) -> WorkflowState:
        """节点 4: 检查唯一任务"""
        count = state["context"].get("task_count", 0)
        unique = count == 1
        
        log_workflow_node(self.logger, "check_unique", "condition", "running", f"检查唯一任务：count={count}")
        
        state["messages"].append(f"检查唯一任务：{'true' if unique else 'false'} (count={count})")
        state["context"]["unique"] = unique
        state["current_node"] = "check_unique"
        
        if not unique:
            state["errors"].append(f"任务数量不唯一：{count}")
            log_workflow_node(self.logger, "check_unique", "condition", "error", f"任务数量不唯一：{count}")
        else:
            log_workflow_node(self.logger, "check_unique", "condition", "success", "唯一任务检查通过")
        
        return state
    
    async def _query_schedule_node(self, state: WorkflowState) -> WorkflowState:
        """节点 5: 查询调度配置 - 调用 Mock 服务 API"""
        task_id = state["context"].get("task_id", "task_001")
        
        log_workflow_node(self.logger, "query_schedule", "skill_call", "running", f"查询调度：task_id={task_id}")
        
        try:
            schedule = await self.mock_client.get_schedule_by_task(task_id)
            
            if schedule:
                state["context"]["schedule_info"] = schedule
                state["context"]["schedule_id"] = schedule.get("schedule_id")
                state["messages"].append(f"当前调度：{schedule.get('cron_expression')}")
                log_workflow_node(self.logger, "query_schedule", "skill_call", "success", f"查询到调度：{schedule.get('cron_expression')}", schedule)
            else:
                state["context"]["schedule_info"] = None
                state["messages"].append("调度配置不存在")
                state["errors"].append("调度配置不存在")
                log_workflow_node(self.logger, "query_schedule", "skill_call", "error", "调度配置不存在")
        except NetworkError as e:
            state["errors"].append(f"网络错误：{e.message}")
            log_workflow_node(self.logger, "query_schedule", "skill_call", "error", f"网络错误：{e.message}")
        except Exception as e:
            state["errors"].append(f"未知错误：{str(e)}")
            log_workflow_node(self.logger, "query_schedule", "skill_call", "error", f"未知错误：{str(e)}")
        
        state["current_node"] = "query_schedule"
        return state
    
    async def _user_confirm_node(self, state: WorkflowState) -> WorkflowState:
        """节点 6: 用户确认"""
        new_cron = state["input"].get("new_cron", "0 0 * * *")
        schedule_info = state["context"].get("schedule_info", {})
        old_cron = schedule_info.get("cron_expression", "unknown")
        
        log_workflow_node(self.logger, "user_confirm", "user_confirm", "running", f"等待用户确认：{old_cron} -> {new_cron}")
        
        state["messages"].append(f"等待用户确认：{old_cron} -> {new_cron}")
        state["context"]["user_confirmed"] = True
        state["current_node"] = "user_confirm"
        
        log_workflow_node(self.logger, "user_confirm", "user_confirm", "success", "用户已确认")
        return state
    
    async def _update_schedule_node(self, state: WorkflowState) -> WorkflowState:
        """节点 7: 更新调度 - 调用 Mock 服务 API"""
        schedule_id = state["context"].get("schedule_id", "schedule_001")
        new_cron = state["input"].get("new_cron", "0 0 * * *")
        new_description = state["input"].get("new_description", "更新后的调度")
        
        log_workflow_node(self.logger, "update_schedule", "skill_call", "running", f"更新调度：{schedule_id} -> {new_cron}")
        
        try:
            updates = {
                "cron_expression": new_cron,
                "cron_description": new_description
            }
            result = await self.mock_client.update_schedule(schedule_id, updates)
            
            if result.get("success"):
                state["context"]["schedule_updated"] = True
                state["context"]["old_cron"] = result.get("old_config", {}).get("cron_expression")
                state["context"]["new_cron"] = result.get("new_config", {}).get("cron_expression")
                state["messages"].append(f"调度更新成功：{state['context']['old_cron']} -> {state['context']['new_cron']}")
                log_workflow_node(self.logger, "update_schedule", "skill_call", "success", f"调度更新成功", {"old": state['context']['old_cron'], "new": state['context']['new_cron']})
            else:
                state["context"]["schedule_updated"] = False
                error_msg = result.get("error", "未知错误")
                state["messages"].append(f"调度更新失败：{error_msg}")
                state["errors"].append(f"调度更新失败：{error_msg}")
                log_workflow_node(self.logger, "update_schedule", "skill_call", "error", f"调度更新失败：{error_msg}")
        except NetworkError as e:
            state["errors"].append(f"网络错误：{e.message}")
            state["context"]["schedule_updated"] = False
            log_workflow_node(self.logger, "update_schedule", "skill_call", "error", f"网络错误：{e.message}")
        except Exception as e:
            state["errors"].append(f"未知错误：{str(e)}")
            state["context"]["schedule_updated"] = False
            log_workflow_node(self.logger, "update_schedule", "skill_call", "error", f"未知错误：{str(e)}")
        
        state["current_node"] = "update_schedule"
        return state
    
    async def _verify_running_node(self, state: WorkflowState) -> WorkflowState:
        """节点 8: 验证运行 - 调用 Mock 服务 API"""
        schedule_id = state["context"].get("schedule_id", "schedule_001")
        
        log_workflow_node(self.logger, "verify_running", "skill_call", "running", f"验证运行：{schedule_id}")
        
        try:
            is_running = await self.mock_client.verify_running(schedule_id)
            
            state["context"]["running"] = is_running
            state["messages"].append(f"运行状态：{'running' if is_running else 'stopped'}")
            
            if is_running:
                log_workflow_node(self.logger, "verify_running", "skill_call", "success", "任务正常运行")
            else:
                state["errors"].append("任务未正常运行")
                log_workflow_node(self.logger, "verify_running", "skill_call", "warning", "任务未正常运行")
        except NetworkError as e:
            state["errors"].append(f"网络错误：{e.message}")
            state["context"]["running"] = False
            log_workflow_node(self.logger, "verify_running", "skill_call", "error", f"网络错误：{e.message}")
        except Exception as e:
            state["errors"].append(f"未知错误：{str(e)}")
            state["context"]["running"] = False
            log_workflow_node(self.logger, "verify_running", "skill_call", "error", f"未知错误：{str(e)}")
        
        state["current_node"] = "verify_running"
        return state
    
    async def _end_node(self, state: WorkflowState) -> WorkflowState:
        """节点 9: 结束"""
        success = len(state["errors"]) == 0
        
        log_workflow_node(self.logger, "end", "end", "running" if not success else "success", f"工作流执行完成", {"success": success, "errors": len(state["errors"])})
        
        state["messages"].append("工作流执行完成")
        state["output"]["success"] = success
        state["output"]["completed_at"] = datetime.now().isoformat()
        state["output"]["old_cron"] = state["context"].get("old_cron")
        state["output"]["new_cron"] = state["context"].get("new_cron")
        state["output"]["errors"] = state["errors"]
        state["output"]["warnings"] = state.get("warnings", [])
        state["current_node"] = "end"
        
        if success:
            self.logger.info(f"工作流执行成功：{self.workflow_id}")
        else:
            self.logger.error(f"工作流执行失败：{self.workflow_id} - {state["errors"]}")
        
        return state
    
    async def execute(self, input_data: Dict[str, Any]):
        """执行工作流"""
        self.logger.info(f"工作流开始执行：{self.workflow_id}")
        
        initial_state = {
            "input": input_data,
            "output": {},
            "messages": [],
            "context": {},
            "current_node": "start",
            "errors": [],
            "warnings": []
        }
        
        try:
            async for event in self.graph.astream(initial_state):
                yield event
        except IntelligentDataLakeError as e:
            self.logger.error(f"工作流业务异常：{e.to_dict()}")
            raise
        except Exception as e:
            self.logger.error(f"工作流未知异常：{str(e)}")
            raise


def create_modify_schedule_workflow() -> Workflow:
    """创建"修改调度时间"工作流"""
    return Workflow("wf_modify_schedule_v1", "修改调度时间")


if __name__ == "__main__":
    async def test():
        print("=== LangGraph 工作流引擎测试 (真实 Mock 服务 + 错误处理 + 日志) ===\n")
        workflow = create_modify_schedule_workflow()
        print(f"工作流：{workflow.name}")
        print(f"ID: {workflow.workflow_id}")
        print(f"Mock Base URL: {workflow.mock_client.base_url}\n")
        
        input_data = {
            "db": "aaa",
            "schema": "bbb",
            "table": "ccc",
            "new_cron": "0 0 * * *",
            "new_description": "每天凌晨 0 点执行"
        }
        
        print("执行工作流...")
        async for event in workflow.execute(input_data):
            for node, state in event.items():
                msg = state['messages'][-1] if state['messages'] else ''
                errors = f" (错误：{state['errors']})" if state['errors'] else ''
                warnings = f" (警告：{state['warnings']})" if state.get('warnings') else ''
                print(f"  [{node}] {msg}{errors}{warnings}")
        
        print(f"\n最终状态：完成")
    
    asyncio.run(test())
