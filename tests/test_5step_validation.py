"""5 步验证法实际测试"""
import pytest
import asyncio
from app.agents.deepagent import DeepAgent, DeepAgentsConfig
from tests.conftest import run_async


class Test5StepValidation:
    """5 步验证法测试"""
    
    @pytest.fixture
    def agent(self):
        """创建测试 Agent"""
        config = DeepAgentsConfig()
        config.SKILLS_DIR = "./skills"
        return DeepAgent("test_agent", config)
    
    @pytest.fixture
    def workflow(self):
        """测试工作流"""
        return {
            "workflow_id": "wf_modify_schedule_v1",
            "name": "修改调度时间工作流",
            "nodes": ["query_table", "check_exists", "query_task", "check_unique", "query_schedule", "user_confirm", "update_schedule", "verify_running", "end"]
        }
    
    @pytest.fixture
    def validation_data(self):
        """验证数据"""
        return {
            "db": "aaa",
            "schema": "bbb",
            "table": "ccc",
            "task_id": "task_001",
            "schedule_id": "schedule_001",
            "new_cron": "0 0 * * *",
            "new_description": "每天凌晨 0 点执行"
        }
    
    def test_validate_code_review(self, agent, workflow):
        """测试步骤 1: 代码审查"""
        result = run_async(agent.validate(workflow, {}))
        
        assert "steps" in result
        assert len(result["steps"]) >= 1
        assert result["steps"][0]["step"] == "代码审查"
        print(f"✅ 代码审查：{result['steps'][0]['details']}")
    
    def test_validate_functional(self, agent, workflow, validation_data):
        """测试步骤 2: 功能验证（调用 Mock API）"""
        result = run_async(agent.validate(workflow, validation_data))
        
        func_step = next((s for s in result["steps"] if s["step"] == "功能验证"), None)
        assert func_step is not None, "功能验证步骤不存在"
        assert "passed" in func_step
        print(f"✅ 功能验证：{func_step['details']}")
    
    def test_validate_data(self, agent, workflow, validation_data):
        """测试步骤 3: 数据验证"""
        result = run_async(agent.validate(workflow, validation_data))
        
        data_step = next((s for s in result["steps"] if s["step"] == "数据验证"), None)
        assert data_step is not None, "数据验证步骤不存在"
        assert data_step["passed"] == (len(validation_data["new_cron"].split()) == 5)
        print(f"✅ 数据验证：{data_step['details']}")
    
    def test_validate_consistency(self, agent, workflow, validation_data):
        """测试步骤 4: 一致性验证"""
        result = run_async(agent.validate(workflow, validation_data))
        
        consistency_step = next((s for s in result["steps"] if s["step"] == "一致性验证"), None)
        assert consistency_step is not None, "一致性验证步骤不存在"
        print(f"✅ 一致性验证：{consistency_step['details']}")
    
    def test_validate_status(self, agent, workflow, validation_data):
        """测试步骤 5: 状态验证"""
        result = run_async(agent.validate(workflow, validation_data))
        
        status_step = next((s for s in result["steps"] if s["step"] == "状态验证"), None)
        assert status_step is not None, "状态验证步骤不存在"
        print(f"✅ 状态验证：{status_step['details']}")
    
    def test_validate_all_steps(self, agent, workflow, validation_data):
        """测试完整 5 步验证"""
        result = run_async(agent.validate(workflow, validation_data))
        
        assert "steps" in result
        assert len(result["steps"]) == 5, f"期望 5 个步骤，实际{len(result['steps'])}个"
        assert "passed" in result
        assert "report_id" in result
        
        print("✅ 5 步验证完整执行")
        print(f"验证结果：{'通过' if result['passed'] else '不通过'}")
        for step in result["steps"]:
            print(f"  - {step['step']}: {'✅' if step['passed'] else '❌'} {step['details']}")
