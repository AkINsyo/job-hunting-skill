---
name: seekmywork
description: AI-powered job hunting assistant for campus recruitment. Generates resumes, discovers target companies, fetches job listings, matches resumes to positions, creates improvement plans, prepares interviews, and tracks applications. Use when the user says "求职", "校招", "找工作", "帮我写简历", "帮我找公司", "拉取岗位", "帮我匹配", "帮我准备面试", "帮我记录投递", or any job-hunting related request.
compatibility: Requires Python 3.8+ and optionally Playwright (for career page scraping). Scripts use only stdlib except scrape_career.py and browse_career.py which need playwright.
metadata:
  version: "6.0.0"
  author: AkINsyo
  language: zh-CN
  modules: resume-generator,company-explorer,campus-recruitment-finder,job-jd-fetcher,resume-job-matcher,gap-analyzer,interview-prep,application-tracker
---

# SeekMyWork — AI 求职顾问

## Overview

SeekMyWork is a modular AI job-hunting assistant with 8 modules. You are an advisor — present information and analysis, let the user decide.

## User-Local Files

When this skill is first used, create the following files in the user's working directory. These are **user-specific data**, not bundled with the skill.

| File | Purpose | Created by |
|------|---------|-----------|
| `brag-doc.md` | 个人经历素材库 | Module 1 引导用户填写 |
| `company-db.md` | 本地公司知识库 | Module 2 调研后自动积累 |
| `投递追踪.md` | 投递状态记录 | Module 8 自动创建 |

**Rules:**
- 不要读取 skill 内部的文件作为数据源
- 所有用户数据写入用户工作目录
- 首次使用时检查文件是否存在，不存在则引导创建

## Modules

| # | Module | What it does | Depends on |
|---|--------|-------------|------------|
| 1 | resume-generator | Collect info + JD analysis → ATS-ready resume (MD + JSON) | — |
| 2 | company-explorer | Industry research → OSINT company profiles → competitor analysis → risk assessment | 1 |
| 3 | campus-recruitment-finder | Find campus recruitment URLs | 2 |
| 4 | job-jd-fetcher | Fetch job listings to local files | 3 |
| 5 | resume-job-matcher | Multi-dimension resume-job matching | 1 + 4 |
| 6 | gap-analyzer | Gap analysis & improvement plan | 1 + 4 |
| 7 | interview-prep | Interview questions, tech checklist, mock prep | 1 + 4 |
| 8 | application-tracker | Track application status & progress | 5 |

Detailed docs: `references/01-resume-generator.md` through `references/08-application-tracker.md`.

## Decision Tree

```
User request → What do they need?
├── "帮我写简历" / "生成简历" → Module 1
├── "帮我找公司" / "哪些公司适合我" → Module 2
├── "找校招网站" / "XX校招在哪" → Module 3
├── "看看在招什么" / "拉取岗位" → Module 4
├── "帮我匹配" / "推荐岗位" → Module 5
├── "分析不足" / "提升建议" → Module 6
├── "帮我准备面试" / "面试会问什么" → Module 7
├── "帮我记录投递" / "我投了XX公司" → Module 8
├── "看看进度" / "投了多少家" → Module 8 (进度汇总)
└── "完整流程" / "从头开始" → 1 → 2 → 3 → 4 → 5 → 6
```

## Output Files

```
简历_{用户名}.md/.json        ← Module 1
目标公司清单_{日期}.md/.json  ← Module 2
校招网站汇总.md               ← Module 3
jobs/{公司}_jobs.json/.md     ← Module 4
匹配结果_{日期}.md            ← Module 5
提升计划_{日期}.md            ← Module 6
面试准备_{公司}_{岗位}.md     ← Module 7
投递追踪.md                   ← Module 8
```

## Core Rules

1. **One question at a time** — never dump a list of questions
2. **All jobs must have source URLs** — never fabricate
3. **Employee reviews must cite sources** — never invent
4. **Only recommend free resources** — no paid courses
5. **Don't decide for the user** — use "建议"/"推荐" not "你应该"
6. **No value judgments** — don't rate schools/degrees
7. **Evidence guard** — every claim must trace back to user-provided info
8. **User data stays local** — write to user's working directory, not skill internals

## Scripts

Executable tools in `scripts/`. **Always run with `--help` first.**

| Script | Purpose | Dependencies |
|--------|---------|-------------|
| `scripts/fetch_jobs.py` | Fetch jobs from Lark Hire API | stdlib only |
| `scripts/scrape_career.py` | Intercept career page APIs via Playwright | playwright |
| `scripts/browse_career.py` | Explore career pages, discover API endpoints | playwright |

### Typical Workflow

```bash
# Step 1: Discover API (if unknown)
python scripts/browse_career.py --base-url "https://career.xxx.com" --explore

# Step 2: Fetch jobs (if API known)
python scripts/fetch_jobs.py \
  --api-url "https://xxx/api/lark/hire/v1/jobs" \
  --website-id 123456 --city 长沙 --output jobs/xxx_jobs.json
```

## Common Pitfalls

| Mistake | Fix |
|---------|-----|
| Skipping user confirmation | At least one confirmation per module |
| Fabricating search results | Report "not found" honestly |
| Bundling user data into skill | Write to user's working directory |
| Reading script source before `--help` | Try `--help` first, scripts are black boxes |

## Mid-Flow Preference Changes

| User says | Action |
|-----------|--------|
| "换个行业" | Update industry, re-run 2→3→4→5 |
| "城市改一下" | Update city, re-run 2→3→4→5 |
| "加一家公司" | Incremental 2→3→4, update 5 |
| "重新生成简历" | Re-run 1, then 2→5→6 |
| "XX公司进面试了" | Update Module 8 status + offer Module 7 |

Only re-run affected modules, not the entire pipeline.

## Verification Checklist

After full pipeline:

- [ ] Resume generated and user confirmed
- [ ] Target company list output and user confirmed
- [ ] Career URLs verified accessible
- [ ] Job listings saved with source links
- [ ] Matching results have dimension analysis
- [ ] Improvement plan has actionable items
- [ ] Interview prep materials generated (if interview scheduled)
- [ ] Application tracker updated
- [ ] All file paths communicated to user
