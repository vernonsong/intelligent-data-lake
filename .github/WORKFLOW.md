# 智能体协作工作流 - 强制机制

**版本:** 1.0  
**生效日期:** 2026-03-16  
**状态:** 强制使用

---

## 核心原则：零信任验证

**不信任任何报告，只信任：**
1. ✅ 直接 API 调用验证
2. ✅ 直接测试运行结果
3. ✅ 直接日志检查
4. ✅ 直接代码审查

---

## 开发流程（强制）

### 1. 任务分配（使用模板）

**Main Agent 必须：**
- [ ] 使用 `.github/TASK_TEMPLATE.md`
- [ ] 明确文件路径、函数名、检查内容
- [ ] 明确输出要求、验证方式
- [ ] 明确完成标准

**否则 Agent 可以拒绝执行！**

### 2. 开发执行

**Developer 必须：**
- [ ] 编写代码
- [ ] 编写测试（核心功能 100% 覆盖）
- [ ] 运行测试并记录结果
- [ ] 提交代码（包含测试）

### 3. 代码审查（使用清单）

**Reviewer 必须：**
- [ ] 使用 `.github/CODE_REVIEW_CHECKLIST.md`
- [ ] 逐项检查并打勾/叉
- [ ] 运行测试验证
- [ ] 给出评分和结论
- [ ] **审查报告必须包含验证命令和输出**

**否则审查无效！**

### 4. 测试验证（强制覆盖率）

**QA 必须：**
- [ ] 运行 `pytest tests/ -v --cov=app`
- [ ] 检查覆盖率（核心 100%，整体 70%+）
- [ ] 分析失败测试
- [ ] **测试报告必须包含覆盖率报告**

**否则测试无效！**

### 5. PM 验收（零信任）

**PM 必须：**
- [ ] 直接调用 API 验证功能
- [ ] 查看后端日志验证真实调用
- [ ] 检查测试报告验证覆盖率
- [ ] 检查审查报告验证清单完成
- [ ] **验收报告必须包含 API 调用输出和日志片段**

**否则验收无效！**

### 6. Main Agent 最终验证（零信任）

**Main Agent 必须：**
- [ ] 随机抽查 API 调用
- [ ] 随机抽查测试运行
- [ ] 随机抽查代码片段
- [ ] 验证所有报告真实性
- [ ] **验证记录必须存档**

**否则交付无效！**

---

## 问责机制

### 问题分级

| 级别 | 定义 | 处理 |
|------|------|------|
| **P0 - 伪造** | 代码/测试/报告造假 | 立即开除 + 追溯责任 |
| **P1 - 失职** | 未按流程执行 | 警告 + 重新执行 |
| **P2 - 疏忽** | 遗漏检查项 | 提醒 + 补充检查 |

### 处理流程

```
发现问题
  ↓
调查根因（是伪造/失职/疏忽？）
  ↓
P0: 立即开除 + 追溯责任
    - 删除 Agent 配置
    - 追溯所有经手代码
    - 重新验证所有报告
    
P1: 警告 + 重新执行
    - 记录警告
    - 强制重新执行流程
    - Main Agent 监督
    
P2: 提醒 + 补充检查
    - 口头提醒
    - 补充遗漏检查
```

### 追溯机制

**所有报告必须包含：**
- 执行时间戳
- 执行命令
- 执行输出
- 验证人签名

**Main Agent 随机抽查：**
- 每周抽查 3 个报告
- 重新执行验证命令
- 对比输出一致性
- 发现不一致立即调查

---

## 自动化验证（CI/CD）

### GitHub Actions 配置

```yaml
name: Zero Trust CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Tests
        run: pytest tests/ -v --cov=app --cov-report=xml
      
      - name: Check Coverage
        run: |
          # 核心模块必须 100%
          coverage report --include="app/agents/deepagent.py" --fail-under=100
          coverage report --include="app/workflows/workflow.py" --fail-under=100
          # 整体 70%
          coverage report --fail-under=70
      
      - name: API Verification
        run: |
          # 启动服务
          uvicorn app.main:app &
          sleep 5
          # 调用 API 验证
          curl -X POST http://localhost:8000/api/v1/orchestration/create ...
          curl -X POST http://localhost:8000/api/v1/validation/validate ...
      
      - name: Report Verification
        run: |
          # 验证报告是否存在
          test -f shared/reports/审查报告-*.md
          test -f shared/reports/测试报告-*.md
          # 验证报告是否包含验证命令
          grep -q "验证命令" shared/reports/审查报告-*.md
          grep -q "覆盖率" shared/reports/测试报告-*.md
```

### 门禁规则

- ❌ 测试失败 → 阻止合并
- ❌ 覆盖率不达标 → 阻止合并
- ❌ 报告缺失 → 阻止合并
- ❌ 验证命令缺失 → 阻止合并
- ❌ API 验证失败 → 阻止合并

---

## 持续改进

### 每周回顾

**Main Agent 必须：**
- [ ] 统计本周问题数量
- [ ] 分析问题类型（伪造/失职/疏忽）
- [ ] 识别流程漏洞
- [ ] 更新机制文档

### 每月审计

**Main Agent 必须：**
- [ ] 随机抽查 10 个历史报告
- [ ] 重新执行验证
- [ ] 对比一致性
- [ ] 发现伪造立即处理
- [ ] 更新审查清单

---

**生效日期:** 2026-03-16  
**执行状态:** 强制  
**违反处理:** 按问责机制处理
