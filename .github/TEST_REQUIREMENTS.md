# 测试覆盖率要求

**版本:** 1.0  
**生效日期:** 2026-03-16  
**状态:** 强制使用

---

## 最低覆盖率要求

| 模块 | 最低覆盖率 | 状态检查 |
|------|-----------|---------|
| **核心业务逻辑** | **100%** | 必须 |
| - deepagent.py (5 步验证) | 100% | 必须 |
| - workflow.py (9 个节点) | 100% | 必须 |
| **API 路由** | **80%** | 必须 |
| - chat.py | 80% | 必须 |
| - orchestration.py | 80% | 必须 |
| - validation.py | 80% | 必须 |
| **工具函数** | **80%** | 必须 |
| - exceptions.py | 80% | 必须 |
| - logging_config.py | 80% | 必须 |
| - mock_data.py | 80% | 必须 |
| **整体项目** | **70%** | 建议 |

---

## 测试质量要求

### 必须测试

- [ ] Happy path（正常流程）
- [ ] 错误场景（异常处理）
- [ ] 边界条件（极限值）
- [ ] 输入验证（非法输入）

### Mock 测试要求

- [ ] 必须说明使用 Mock 的原因
- [ ] Mock 数据必须合理
- [ ] 多组测试数据（不只是 happy path）

### 测试命名规范

```python
def test_xxx_when_yyy():
    """测试当 yyy 时 xxx 的行为"""
    
def test_xxx_with_yyy():
    """测试使用 yyy 时的 xxx"""
    
def test_xxx_raises_yyy():
    """测试 xxx 是否抛出 yyy 异常"""
```

---

## 提交前检查

```bash
# 1. 运行所有测试
pytest tests/ -v

# 2. 生成覆盖率报告
pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html

# 3. 检查覆盖率
# 核心模块必须 100%
coverage report --include="app/agents/deepagent.py" --fail-under=100
coverage report --include="app/workflows/workflow.py" --fail-under=100

# 整体 70%
coverage report --fail-under=70
```

---

## CI/CD 集成

### GitHub Actions

```yaml
name: Test

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.12
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run tests
        run: pytest tests/ -v --cov=app --cov-report=xml
      
      - name: Check coverage
        run: |
          # 核心模块必须 100%
          coverage report --include="app/agents/deepagent.py" --fail-under=100
          coverage report --include="app/workflows/workflow.py" --fail-under=100
          # 整体 70%
          coverage report --fail-under=70
```

### 合并规则

- ❌ 测试失败 → 阻止合并
- ❌ 覆盖率下降 >5% → 阻止合并
- ❌ 核心模块 <100% → 阻止合并
- ❌ 整体 <70% → 警告

---

## 测试报告格式

```markdown
# 测试报告 -XXX

**测试时间:** [YYYY-MM-DD HH:MM]
**测试人:** [Agent 名称]
**测试范围:** [模块/功能]

## 测试结果

| 测试文件 | 通过 | 失败 | 总计 | 通过率 |
|---------|------|------|------|--------|
| xxx.py | X | X | X | XX% |

## 覆盖率

| 模块 | 覆盖率 | 要求 | 状态 |
|------|--------|------|------|
| deepagent.py | XX% | 100% | ✅/❌ |
| workflow.py | XX% | 100% | ✅/❌ |

## 失败测试分析

| 测试 | 失败原因 | 修复建议 |
|------|---------|---------|
| xxx | ... | ... |

## 结论

[通过/不通过] + 理由
```

---

**强制要求:**
- 所有代码提交必须有测试
- 核心功能必须 100% 覆盖
- 测试报告必须包含覆盖率
- Main Agent 必须验证覆盖率达标
