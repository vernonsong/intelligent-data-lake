# 智能入湖系统

**版本:** 0.1.0  
**创建日期:** 2026-03-15

---

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境

```bash
cp .env.example .env
# 编辑 .env 文件，填入 AI_MODEL_API_KEY 等配置
```

### 3. 运行服务

```bash
# 开发模式
python -m app.main

# 或
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问 API

- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

---

## 项目结构

```
intelligent-data-lake/
├── app/
│   ├── main.py              # FastAPI 入口
│   ├── api/v1/
│   │   ├── chat.py          # 聊天接口
│   │   ├── orchestration.py # 编排接口
│   │   ├── validation.py    # 验证接口
│   │   ├── skills.py        # Skill 管理
│   │   └── mock.py          # Mock 服务
│   ├── agents/              # 智能体
│   ├── skills/              # Skill 运行时
│   ├── workflows/           # 工作流
│   ├── services/            # 服务层
│   ├── models/              # 数据模型
│   ├── config/
│   │   └── settings.py      # 应用配置
│   └── utils/               # 工具
├── requirements.txt
├── .env.example
└── README.md
```

---

## 配置说明

### 必需配置 (.env)

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `AI_MODEL_API_KEY` | AI 模型 API Key | `sk-xxx` |
| `AI_MODEL_ENDPOINT` | AI 模型端点 | `https://api.example.com` |
| `AI_MODEL_NAME` | 模型名称 | `qwen3.5-plus` |

---

**状态:** 项目框架已初始化  
**最后更新:** 2026-03-15
