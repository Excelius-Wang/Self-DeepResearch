# Self-DeepResearch

<p align="center">
  <img src="frontend/public/favicon.svg" alt="DeepResearch Logo" width="80" height="80">
</p>

<p align="center">
  <strong>基于 LangGraph 和 Tavily 的自主深度研究智能体</strong>
</p>

<p align="center">
  <a href="#功能特性">功能特性</a> •
  <a href="#系统架构">系统架构</a> •
  <a href="#快速开始">快速开始</a> •
  <a href="#配置说明">配置说明</a> •
  <a href="#技术栈">技术栈</a> •
  <a href="#开源协议">开源协议</a>
</p>

---

## 项目简介

Self-DeepResearch 是一个 AI 驱动的自主研究助手，能够针对任意主题进行规划、搜索、反思，并生成全面的研究报告。系统采用多智能体工作流，通过迭代优化确保输出高质量、有据可查的研究成果。

## 功能特性

- **自主研究工作流** - 多智能体系统自动规划查询、搜索网络、审查结果，并迭代优化直至满意
- **实时流式输出** - 通过精美的思维链可视化界面，实时观察研究过程的展开
- **迭代式优化** - 内置审查智能体评估研究结果，在需要时请求补充研究
- **来源溯源** - 所有研究笔记均包含来源链接，便于核实和延伸阅读
- **历史记录** - 保存并回顾过往研究会话，包含完整上下文
- **深色模式** - 支持自动主题检测，保护眼睛
- **导出功能** - 支持下载 Markdown 格式或打印为 PDF

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                          用户输入                                │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       规划智能体 (Planner)                        │
│                    将任务分解为多个子查询                          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      研究智能体 (Researcher)                      │
│               通过 Tavily 搜索网络，提取关键笔记                    │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       审查智能体 (Reviewer)                       │
│              评估研究完整性，必要时请求补充研究                      │
└─────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
               需要补充？                 已满足？
                    │                       │
                    ▼                       ▼
             返回研究智能体          ┌─────────────────┐
                                    │ 报告智能体       │
                                    │ (Reporter)      │
                                    │ 生成最终报告     │
                                    └─────────────────┘
```

## 快速开始

### 环境要求

- **Node.js** >= 18
- **Python** >= 3.10
- **OpenAI API Key**（或兼容的 API 端点）
- **Tavily API Key**（[点击获取](https://tavily.com/)）

### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/Self-DeepResearch.git
cd Self-DeepResearch
```

### 2. 后端配置

```bash
cd backend

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows 系统: .venv\Scripts\activate

# 安装依赖
pip install -e .

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 API 密钥

# 启动服务
uvicorn src.main:app --reload --port 8000
```

### 3. 前端配置

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 4. 访问应用

在浏览器中打开 `http://localhost:5173`

## 配置说明

### 后端环境变量

在 `backend/` 目录下创建 `.env` 文件：

```env
# OpenAI API 配置
OPENAI_API_KEY=your-api-key
OPENAI_MODEL_NAME=gpt-4o
OPENAI_API_BASE=https://api.openai.com/v1  # 可选：自定义 API 端点

# Tavily 搜索 API
TAVILY_API_KEY=your-tavily-key

# 应用设置
LOG_LEVEL=INFO
```

### 前端环境变量

前端使用 Vite 环境变量：

- `.env` - 开发环境配置
- `.env.production` - 生产环境配置

```env
VITE_API_BASE_URL=http://localhost:8000
```

## 技术栈

### 后端
| 技术 | 说明 |
|------|------|
| [FastAPI](https://fastapi.tiangolo.com/) | 高性能异步 Web 框架 |
| [LangGraph](https://github.com/langchain-ai/langgraph) | 多智能体工作流编排 |
| [LangChain](https://langchain.com/) | LLM 应用开发框架 |
| [Tavily](https://tavily.com/) | AI 优化的搜索 API |
| [SQLModel](https://sqlmodel.tiangolo.com/) | 结合 Pydantic 的 SQL 数据库 |

### 前端
| 技术 | 说明 |
|------|------|
| [Vue 3](https://vuejs.org/) | 渐进式 JavaScript 框架 |
| [Vite](https://vitejs.dev/) | 新一代前端构建工具 |
| [Tailwind CSS](https://tailwindcss.com/) | 原子化 CSS 框架 |
| [Lucide Icons](https://lucide.dev/) | 精美开源图标库 |

## 项目结构

```
Self-DeepResearch/
├── backend/
│   ├── src/
│   │   ├── agents/          # LangGraph 智能体节点
│   │   │   ├── planner.py   # 查询分解
│   │   │   ├── researcher.py # 网络搜索与笔记提取
│   │   │   ├── reviewer.py  # 质量评估
│   │   │   └── reporter.py  # 报告生成
│   │   ├── core/            # 配置与 LLM 设置
│   │   ├── tools/           # Tavily 搜索集成
│   │   ├── graph.py         # LangGraph 工作流定义
│   │   ├── main.py          # FastAPI 应用入口
│   │   └── models.py        # Pydantic/状态模型
│   └── pyproject.toml
│
├── frontend/
│   ├── src/
│   │   ├── components/      # Vue 组件
│   │   │   ├── ResearchForm.vue    # 研究表单
│   │   │   ├── ThoughtChain.vue    # 思维链展示
│   │   │   ├── ReportView.vue      # 报告视图
│   │   │   └── HistorySidebar.vue  # 历史侧边栏
│   │   ├── composables/     # Vue 组合式函数
│   │   ├── App.vue          # 主应用
│   │   └── types.ts         # TypeScript 类型定义
│   └── package.json
│
└── README.md
```

## API 接口

| 方法 | 端点 | 说明 |
|------|------|------|
| `POST` | `/research/stream` | 启动新的研究会话（SSE 流式） |
| `GET` | `/history` | 获取所有研究历史 |
| `GET` | `/history/:id` | 获取指定研究会话 |
| `DELETE` | `/history/:id` | 删除指定会话 |
| `GET` | `/health` | 健康检查 |

## 参与贡献

欢迎贡献代码！请随时提交 Pull Request。

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m '添加某个很棒的特性'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 发起 Pull Request

## 开源协议

本项目基于 MIT 协议开源 - 详见 [LICENSE](LICENSE) 文件。

---

<p align="center">
  由 <a href="https://github.com/excelius">Excelius</a> 用 ❤️ 打造
</p>
