"""工作流节点实际测试"""
import pytest
import asyncio
from app.workflows.workflow import Workflow, WorkflowState
from tests.conftest import run_async


class TestWorkflowNodes:
    """工作流节点测试"""
    
    @pytest.fixture
    def workflow(self):
        """创建工作流"""
        return Workflow("wf_modify_schedule_v1", "修改调度时间工作流")
    
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
        
        assert "table_info" in result["context"] or "exists" in result["context"]
        assert len(result["messages"]) > 0
        print(f"✅ query_table: {result['messages'][-1]}")
    
    def test_check_exists_node(self, workflow, initial_state):
        """测试节点 2: 检查表存在"""
        # 先执行 query_table
        state = run_async(workflow._query_table_node(initial_state))
        # 再执行 check_exists
        result = run_async(workflow._check_exists_node(state))
        
        assert "exists" in result["context"]
        print(f"✅ check_exists: 表{'存在' if result['context']['exists'] else '不存在'}")
    
    def test_query_task_node(self, workflow, initial_state):
        """测试节点 3: 查询集成任务"""
        state = run_async(workflow._query_table_node(initial_state))
        result = run_async(workflow._query_task_node(state))
        
        assert "tasks" in result["context"] or "task_count" in result["context"]
        print(f"✅ query_task: 找到{result['context'].get('task_count', 0)}个任务")
    
    def test_check_unique_node(self, workflow, initial_state):
        """测试节点 4: 检查唯一任务"""
        state = run_async(workflow._query_table_node(initial_state))
        state = run_async(workflow._query_task_node(state))
        result = run_async(workflow._check_unique_node(state))
        
        assert "unique" in result["context"]
        print(f"✅ check_unique: 任务{'唯一' if result['context']['unique'] else '不唯一'}")
    
    def test_query_schedule_node(self, workflow, initial_state):
        """测试节点 5: 查询调度配置"""
        state = run_async(workflow._query_table_node(initial_state))
        state = run_async(workflow._query_task_node(state))
        result = run_async(workflow._query_schedule_node(state))
        
        assert "schedule_info" in result["context"] or "schedule_id" in result["context"]
        print(f"✅ query_schedule: {result['messages'][-1]}")
    
    def test_full_workflow(self, workflow, initial_state):
        """测试完整工作流执行"""
        # 模拟执行所有节点
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
            print(f"✅ {node_name}: {state['messages'][-1] if state['messages'] else '无消息'}")
        
        assert state["output"].get("success") == True
        print(f"\n✅ 完整工作流执行成功")
        print(f"输出：{state['output']}")
