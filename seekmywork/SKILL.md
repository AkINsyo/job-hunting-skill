---
name: seekmywork
description: AI-powered job hunting assistant for campus recruitment. Generates resumes, discovers target companies, fetches job listings, matches resumes to positions, and creates improvement plans. Use when the user says "求职", "校招", "找工作", "帮我写简历", "帮我找公司", "拉取岗位", "帮我匹配", or any job-hunting related request.
compatibility: Requires Python 3.8+ and optionally Playwright (for career page scraping). Scripts use only stdlib except scrape_career.py and browse_career.py which need playwright.
metadata:
  version: "4.0.0"
  author: AkINsyo
  language: zh-CN
  modules: resume-generator,company-explorer,campus-recruitment-finder,job-jd-fetcher,resume-job-matcher,gap-analyzer
---

# SeekMyWork — AI 求职顾问

## Overview

SeekMyWork is a modular AI job-hunting assistant with 6 modules that can run independently or as a pipeline. You are an advisor — present information and analysis, let the user decide.

## Modules

| # | Module | What it does | Depends on |
|---|--------|-------------|------------|
| 1 | resume-generator | Collect info + JD analysis → generate ATS-ready resume (MD + JSON) | — |
| 2 | company-explorer | Industry research → company screening → employee reviews | 1 |
| 3 | campus-recruitment-finder | Find campus recruitment URLs | 2 |
| 4 | job-jd-fetcher | Fetch job listings to local files | 3 |
| 5 | resume-job-matcher | Multi-dimension resume-job matching | 1 + 4 |
| 6 | gap-analyzer | Gap analysis & improvement plan | 1 + 4 |

Detailed docs for each module: `references/01-resume-generator.md` through `references/06-gap-analyzer.md`.

## Decision Tree

```
User request → What do they need?
├── "帮我写简历" / "生成简历" → Module 1 (references/01-resume-generator.md)
├── "帮我找公司" / "哪些公司适合我" → Module 2 (references/02-company-explorer.md)
├── "找校招网站" / "XX校招在哪" → Module 3 (references/03-campus-recruitment-finder.md)
├── "看看在招什么" / "拉取岗位" → Module 4 (references/04-job-jd-fetcher.md)
├── "帮我匹配" / "推荐岗位" → Module 5 (references/05-resume-job-matcher.md)
│   └── Check: resume exists? jobs exist? → Run missing modules first
├── "分析不足" / "提升建议" → Module 6 (references/06-gap-analyzer.md)
└── "完整流程" / "从头开始" → 1 → 2 → 3 → 4 → 5 → 6
```

## Output Files

```
简历_{用户名}.md              ← Module 1
目标公司清单_{日期}.md        ← Module 2
校招网站汇总.md               ← Module 3
jobs/{公司}_jobs.json/.md     ← Module 4
匹配结果_{日期}.md            ← Module 5
提升计划_{日期}.md            ← Module 6
```

## Core Rules

1. **One question at a time** — never dump a list of questions
2. **All jobs must have source URLs** — never fabricate
3. **Employee reviews must cite sources** — never invent
4. **Only recommend free resources** — no paid courses
5. **Don't decide for the user** — use "建议"/"推荐" not "你应该"
6. **No value judgments** — don't rate schools/degrees

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

# Or scrape directly from career page
python scripts/scrape_career.py \
  --url "https://career.xxx.com/campus" \
  --click-text "投递岗位" --output jobs/xxx_jobs.json

# Batch fetch from config
python scripts/fetch_jobs.py --config assets/companies.json --output-dir jobs/
```

### Lark Hire API Notes

- `page_size` max is 20 (error 99992402 if exceeded)
- Pagination via `page_token` + `has_more`
- City filter via `city_code` (e.g. CT_20 = Changsha)
- Common API path: `*/api/lark/hire/v1/jobs`

## Common Pitfalls

| Mistake | Fix |
|---------|-----|
| Skipping user confirmation | At least one confirmation per module |
| Fabricating search results | Report "not found" honestly |
| Running all modules when only one needed | Only re-run affected modules |
| Reading script source before running `--help` | Try `--help` first, scripts are black boxes |

## Mid-Flow Preference Changes

| User says | Action |
|-----------|--------|
| "换个行业" | Update industry, re-run 2→3→4→5 |
| "城市改一下" | Update city, re-run 2→3→4→5 |
| "加一家公司" | Incremental 2→3→4, update 5 |
| "重新生成简历" | Re-run 1, then 2→5→6 |

Only re-run affected modules, not the entire pipeline.

## Verification Checklist

After full pipeline:

- [ ] Resume generated and user confirmed
- [ ] Target company list output and user confirmed
- [ ] Career URLs verified accessible
- [ ] Job listings saved with source links
- [ ] Matching results have dimension analysis
- [ ] Improvement plan has actionable items
- [ ] All file paths communicated to user
