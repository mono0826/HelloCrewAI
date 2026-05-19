# HelloCrewAI

基于 [DeepLearning.AI — Multi AI Agent Systems with crewAI](https://learn.deeplearning.ai/courses/multi-ai-agent-systems-with-crewai/) 课程的实践仓库，通过 Jupyter Notebook 逐步学习 **CrewAI** 多智能体框架：从 Agent / Task / Crew 基础，到工具、记忆、协作与综合项目。

[课程视频介绍](https://learn.deeplearning.ai/courses/multi-ai-agent-systems-with-crewai/lesson/wwou5/introduction)

## 课时一览

| 课时 | 目录 | 实践任务场景 | 核心知识点 | 主要 Notebook |
|------|------|--------------|------------|---------------|
| **L2** | `L2/` | 围绕指定主题**调研并撰写文章**（策划 → 写作 → 编辑） | 多智能体系统入门；`Agent` / `Task` / `Crew` 基础；角色（role）、目标（goal）、背景（backstory） | `L2_research_write_article.ipynb` |
| **L3** | `L3/` | **多智能体客户支持**自动化（一线支持 + 质检） | 角色扮演、专注与协作；工具（Tools）；护栏（Guardrails）；记忆（Memory） | `L3_customer_support.ipynb` |
| **L4** | `L4/` | **客户外展营销**：识别高价值潜在客户并个性化触达 | 工具的多用途性、容错与缓存；网页搜索等外部工具集成 | `L4_tools_customer_outreach.ipynb` |
| **L5** | `L5/` | **活动策划**自动化（场地、后勤、营销推广） | `Task` 的深入使用；任务依赖与输出；`crewai_tools` | `L5_tasks_event_planning.ipynb` |
| **L6** | `L6/` | **金融分析**多智能体协作（数据、策略、交易、风控） | 智能体之间的协作与任务传递；分层/流水线式 Crew 设计 | `L6_collaboration_financial_analysis.ipynb` |
| **L7** | `L7/` | **求职申请**定制（岗位调研、画像、简历策略、面试准备） | 综合实战：构建完整多智能体系统 | `L7_job_application_crew.ipynb` |

> *_en.ipynb为原版代码，.ipynb为

## 各课智能体角色（摘要）

| 课时 | 智能体 |
|------|--------|
| L2 | Content Planner、Content Writer、Editor |
| L3 | Senior Support Representative、Support Quality Assurance Specialist |
| L4 | Sales Representative、Lead Sales Representative |
| L5 | Venue Coordinator、Logistics Manager、Marketing and Communications Agent |
| L6 | Data Analyst、Trading Strategy Developer、Trade Advisor、Risk Advisor |
| L7 | Tech Job Researcher、Personal Profiler、Resume Strategist、Engineering Interview Preparer |

## 环境准备

各课时目录下通常包含 `.env`（API 密钥）与 `utils.py`（加载环境变量）。在项目根目录创建虚拟环境并安装依赖：

```bash
uv venv
uv pip install crewai crewai[tools]
```

注：*_en.ipynb使用的是google浏览器，这里做了更改，使用baidu搜索[获取apiKey](https://console.bce.baidu.com/qianfan/ais/console/apiKey)

本地运行 Notebook 前，请在对应课时的 `.env` 中配置 OpenAI API Key；部分课时还需 baidu 第三方 API Key。
