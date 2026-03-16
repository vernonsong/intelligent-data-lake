"""工作流节点测试 - Mock 版本（不依赖实际 HTTP）"""
import pytest
from unittest.mock import AsyncMock, patch
from app.workflows.workflow import Workflow, WorkflowState
from tests.conftest import run_async


class TestWorkflowNodesMock:
    """工作流节点测试（Mock HTTP）"""
    
    @pytest.fixture
    def workflow(self):
        """创建工作流"""
        wf = Workflow("wf_modify_schedule_v1", "修改调度时间工作流")
        # Mock mock_client
        wf.mock_client = AsyncMock()
        wf.mock_client.get_table.return_value = {"table": "ccc", "exists": True}
        wf.mock_client.get_tasks_by_table.return_value = [{"task_id": "task_001"}]
        wf.mock_client.get_schedule_by_task.return_value = {"schedule_id": "schedule_001", "cron": "0 */30 * * *"}
        wf.mock_client.update_schedule.return_value = {"success": True, "old_config": {"cron": "0 */30 * * *"}, "new_config": {"cron": "0 0 * * *"}}
        wf.mock_client.verify_running.return_value = True
        return wf
    
    @pytest.fixture
    def initial_state(self):
        """初始状态"""
        return {
            "input": {
                "db": "aaa",
                "schema": "bbb",
                "table": "ccc",
                "new_cron": "0 0 * * *",
                "new_description": "每天凌晨 0 点执行"
            },
            "output": {},
            "messages": [],
            "context": {},
            "current_node": "",
            "errors": [],
            "warnings": []
        }
    
    def test_query_table_node(self, workflow, initial_state):
        """测试节点 1: 查询表信息"""
        result = run_async(workflow._query_table_node(initial_state))
        
        assert result["context"]["exists"] == True
        assert len(result["messages"]) > 0
        print(f"✅ query_table: {result['messages'][-1]}")
    
    def test_check_exists_node(self, workflow, initial_state):
        """测试节点 2: 检查表存在"""
        state = run_async(workflow._query_table_node(initial_state))
        result = run_async(workflow._check_exists_node(state))
        
        assert result["context"]["exists"] == True
        print(f"✅ check_exists: 表存在")
    
    def test_query_task_node(self, workflow, initial_state):
        """测试节点 3: 查询集成任务"""
        state = run_async(workflow._query_table_node(initial_state))
        result = run_async(workflow._query_task_node(state))
        
        assert result["context"]["task_count"] == 1
        print(f"✅ query_task: 找到 1 个任务")
    
    def test_full_workflow(self, workflow, initial_state):
        """测试完整工作流执行"""
        state = initial_state
        nodes = [
            "_query_table_node",
            "_check_exists_node",
            "_query_task_node",
            "_check_unique_node",
            "_query_schedule_node",
            "_user_confirm_node",
            "_update_schedule_node",
            "_verify_running_node",
            "_end_node"
        ]
        
        for node_name in nodes:
            node_func = getattr(workflow, node_name)
            state = run_async(node_func(state))
            if state['messages']:
                print(f"✅ {node_name}: {state['messages'][-1][:50]}")
        
        assert state["output"]["success"] == True
        print(f"\n✅ 完整工作流执行成功")
        print(f"旧调度：{state['context']['old_cron']}")
        print(f"新调度：{state['context']['new_cron']}")
