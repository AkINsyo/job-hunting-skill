# SeekMyWork

[English](./README.en.md) | 中文

> AI 求职顾问 — 一个遵循 [Agent Skills 规范](https://agentskills.io/specification) 的模块化求职辅助 Skill。

[![Agent Skills](https://skills.sh/b/AkINsyo/job-hunting-skill)](https://skills.sh/AkINsyo/job-hunting-skill)

## 这是什么

SeekMyWork 是一个 AI Agent Skill，帮助应届生/实习生完成从简历生成到岗位匹配的完整求职流程。它由 6 个可独立调用的模块组成，既支持单模块独立使用，也支持全流程链式执行。

**核心理念：AI 是顾问，不是决策者。呈现信息和分析，让用户自己判断。**

## 安装

```bash
npx skills add AkINsyo/job-hunting-skill
```

兼容所有支持 [Agent Skills](https://agentskills.io/specification) 的 Agent（Claude Code、Cursor、Codex、Hermes 等）。

也可以手动安装：将 `seekmywork/` 目录复制到你的 Agent Skills 目录。

## 功能模块

| # | 模块 | 功能 | 触发词示例 |
|---|------|------|-----------|
| 1 | **简历生成** | 采集信息 → 生成结构化 Markdown 简历 | "帮我写简历" |
| 2 | **公司调研** | 行业筛选 → 员工评价 → 推荐清单 | "帮我找公司" |
| 3 | **校招查询** | 查找企业校招官网入口 | "找校招网站" |
| 4 | **岗位拉取** | 从招聘平台拉取 JD 到本地 | "看看在招什么" |
| 5 | **简历匹配** | 多维度匹配打分，排序推荐 | "帮我匹配" |
| 6 | **差距分析 | 识别不足，生成提升计划 | "分析不足" |
| 7 | **面试准备** | 面试题预测 + 技术知识点 + 回答框架 | "帮我准备面试" |
| 8 | **投递追踪** | 记录投递状态 + 进度汇总 | "帮我记录投递" |" |

用户可以说"完整流程"触发全流程，也可以单独调用任一模块。

## 依赖

| 依赖 | 用途 | 必需？ |
|------|------|--------|
| Python 3.8+ | 运行脚本工具 | ✅ |
| [Playwright](https://playwright.dev/python/) | 校招页面抓取 | 仅 scrape/browse 脚本需要 |

```bash
# 仅需要 stdlib 的场景（直接调 API）无需额外安装

# 需要 Playwright 时：
pip install playwright
playwright install chromium
```

## 脚本工具

| 脚本 | 用途 | 依赖 | 典型场景 |
|------|------|------|---------|
| `fetch_jobs.py` | 调用飞书招聘 API 拉取岗位 | stdlib | 已知 API URL + websiteId |
| `scrape_career.py` | Playwright 打开校招页面拦截 XHR | playwright | 已知校招页面 URL |
| `browse_career.py` | 浏览校招页面，发现 API 端点 | playwright | 什么都不知道，先探查 |

> **始终先运行 `--help` 查看用法，不要直接读源码。**

### 典型工作流

```bash
# Step 1: 发现 API
python seekmywork/scripts/browse_career.py \
  --base-url "https://career.xxx.com" --explore

# Step 2: 拉取岗位
python seekmywork/scripts/fetch_jobs.py \
  --api-url "https://xxx/api/lark/hire/v1/jobs" \
  --website-id 123456 --city 长沙 --output jobs/xxx.json

# 或者一步到位
python seekmywork/scripts/scrape_career.py \
  --url "https://career.xxx.com/campus" \
  --click-text "投递岗位" --output jobs/xxx.json

# 批量拉取
python seekmywork/scripts/fetch_jobs.py \
  --config seekmywork/assets/companies.json --output-dir jobs/
```

### 飞书招聘 API 须知

- `page_size` 上限为 20（超过会返回错误 99992402）
- 分页通过 `page_token` + `has_more` 控制
- 城市过滤通过 `city_code`（如 `CT_20` = 长沙）
- 常见 API 路径: `*/api/lark/hire/v1/jobs`

## 项目结构

```
seekmywork/
├── SKILL.md                        # Skill 入口（Agent 加载此文件）
├── scripts/                        # 可执行工具脚本
│   ├── fetch_jobs.py               #   飞书招聘 API 岗位拉取（纯 stdlib）
│   ├── scrape_career.py            #   Playwright 校招页面 API 拦截
│   ├── browse_career.py            #   校招页面浏览 & API 发现
│   └── README.md                   #   脚本使用说明
├── references/                     # 模块详细文档（按需加载）
│   ├── 01-resume-generator.md
│   ├── 02-company-explorer.md
│   ├── 03-campus-recruitment-finder.md
│   ├── 04-job-jd-fetcher.md
│   ├── 05-resume-job-matcher.md
│   ├── 06-gap-analyzer.md
│   ├── 07-interview-prep.md
│   └── 08-application-tracker.md
└── (用户本地文件，首次使用时自动创建)
    ├── brag-doc.md                 # 个人经历素材库
    ├── company-db.md               # 本地公司知识库
    └── 投递追踪.md                  # 投递状态记录
```

## 设计原则

- **渐进式加载** — metadata (~100 tokens) → SKILL.md (<5000 tokens) → references/ (按需)
- **模块化** — 8 个模块可独立使用，也可链式组合
- **脚本即黑盒** — 脚本通过 CLI 参数调用，Agent 无需读源码
- **真实数据** — 所有岗位/评价必须附原始链接，不编造
- **素材库驱动** — 用户本地 `brag-doc.md` 一次填写，简历和面试准备自动复用
- **数据本地化** — 用户数据（素材库、公司库、投递记录）存储在用户工作目录，不打包进 Skill

## 参考项目

本项目在设计过程中参考了以下优秀的 Agent Skill 项目：

### 规范与架构

| 项目 | 说明 | 参考内容 |
|------|------|---------|
| [anthropics/skills](https://github.com/anthropics/skills) | Anthropic 官方 Skill 示例集 | Agent Skills 规范、目录结构、渐进式加载 |
| [agentskills.io](https://agentskills.io/specification) | Agent Skills 开放规范 | frontmatter 标准、scripts/references/assets 约定 |

### 求职类 Skill

| 项目 | ⭐ | 说明 | 参考内容 |
|------|---|------|---------|
| [Paramchoudhary/ResumeSkills](https://github.com/Paramchoudhary/ResumeSkills) | 683 | 20 个细分简历/求职 Skill 合集 | 模块化架构、bullet writing、ATS 优化 |
| [liyupi/yupi-skill](https://github.com/liyupi/yupi-skill) | 312 | 程序员鱼皮知识蒸馏 Skill | 中文求职场景、个人 IP 化 |
| [surapuramakhil-org/Job_search_agent](https://github.com/surapuramakhil-org/Job_search_agent) | 150 | 自动搜索+投递 Agent | 自动化流程设计 |
| [spontaneousai/job-hunt-copilot](https://github.com/spontaneousai/job-hunt-copilot) | 136 | 素材库+定制简历+面试讲稿 | 素材库（Brag Doc）机制 |
| [couragec/LLMInternSkill](https://github.com/couragec/LLMInternSkill) | 113 | LLM 方向实习求职 Skill | Evidence Guard 反编造守卫 |
| [SankaiAI/ats-optimized-resume-agent-skill](https://github.com/SankaiAI/ats-optimized-resume-agent-skill) | 71 | ATS 优化简历 Skill | Gate 门控系统、人性化检查、JSON schema |
| [jason-huanghao/jobradar](https://github.com/jason-huanghao/jobradar) | 39 | 德国+中国科技岗位搜索 | 双市场覆盖 |
| [Jichengyuuuuu/resume-builder-skill](https://github.com/Jichengyuuuuu/resume-builder-skill) | 31 | 中文简历快速生成 | 按岗位动态技能维度、HTML+DOCX 输出 |
| [YIKUAIBANZI/job-hunter](https://github.com/YIKUAIBANZI/job-hunter) | 20 | 批量投递自动化 | JD 匹配打分、投递追踪 |
| [earino/resumasher](https://github.com/earino/resumasher) | 7 | 简历+求职信+面试准备包 | 面试准备模块设计 |
| [REALGSY/offer-catcher](https://github.com/REALGSY/offer-catcher) | 2 | 校招求职匹配智能体 | 校招场景参考 |

感谢以上所有开源项目的贡献。

## License

MIT
