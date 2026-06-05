# SeekMyWork

English | [中文](./README.md)

> AI job hunting advisor — a modular Agent Skill following the [Agent Skills specification](https://agentskills.io/specification).

[![Agent Skills](https://skills.sh/b/AkINsyo/job-hunting-skill)](https://skills.sh/AkINsyo/job-hunting-skill)

## What is this

SeekMyWork is an AI Agent Skill that guides students and new graduates through the full job-hunting pipeline — from resume generation to job matching. It consists of 6 independently usable modules that can also run as a chained pipeline.

**Core principle: AI is an advisor, not a decision-maker. Present information and analysis; let the user decide.**

## Install

```bash
npx skills add AkINsyo/job-hunting-skill
```

Compatible with any agent that supports [Agent Skills](https://agentskills.io/specification) (Claude Code, Cursor, Codex, Hermes, etc.).

Alternatively, copy the `seekmywork/` directory into your agent's skills directory.

## Modules

| # | Module | What it does | Example trigger |
|---|--------|-------------|-----------------|
| 1 | **Resume Generator** | Collect info → generate structured Markdown resume | "帮我写简历" / "generate resume" |
| 2 | **Company Explorer** | Industry research → employee reviews → recommendation list | "帮我找公司" / "find companies" |
| 3 | **Campus Recruitment Finder** | Find campus recruitment URLs | "找校招网站" / "find career pages" |
| 4 | **Job JD Fetcher** | Fetch job listings from recruitment platforms | "看看在招什么" / "fetch jobs" |
| 5 | **Resume-Job Matcher** | Multi-dimension matching and scoring | "帮我匹配" / "match jobs" |
| 6 | **Gap Analyzer** | Identify gaps and create improvement plan | "分析不足" / "gap analysis" |

Users can say "完整流程" (full pipeline) to run all modules sequentially, or invoke any module independently.

## Dependencies

| Dependency | Purpose | Required? |
|-----------|---------|-----------|
| Python 3.8+ | Run script tools | ✅ |
| [Playwright](https://playwright.dev/python/) | Career page scraping | Only for scrape/browse scripts |

```bash
# For stdlib-only scenarios (direct API calls), no extra install needed

# For Playwright:
pip install playwright
playwright install chromium
```

## Script Tools

| Script | Purpose | Dependencies | When to use |
|--------|---------|-------------|-------------|
| `fetch_jobs.py` | Fetch jobs via Lark Hire API | stdlib | API URL + websiteId known |
| `scrape_career.py` | Playwright career page API interceptor | playwright | Career page URL known |
| `browse_career.py` | Explore career pages, discover API endpoints | playwright | Nothing known, discover first |

> **Always run `--help` first. Do not read script source unless necessary.**

### Typical Workflow

```bash
# Step 1: Discover API
python seekmywork/scripts/browse_career.py \
  --base-url "https://career.xxx.com" --explore

# Step 2: Fetch jobs
python seekmywork/scripts/fetch_jobs.py \
  --api-url "https://xxx/api/lark/hire/v1/jobs" \
  --website-id 123456 --city Changsha --output jobs/xxx.json

# Or do it in one step
python seekmywork/scripts/scrape_career.py \
  --url "https://career.xxx.com/campus" \
  --click-text "Apply" --output jobs/xxx.json

# Batch fetch
python seekmywork/scripts/fetch_jobs.py \
  --config seekmywork/assets/companies.json --output-dir jobs/
```

### Lark Hire API Notes

- `page_size` max is 20 (returns error 99992402 if exceeded)
- Pagination via `page_token` + `has_more`
- City filtering via `city_code` (e.g. `CT_20` = Changsha)
- Common API path: `*/api/lark/hire/v1/jobs`

## Project Structure

```
seekmywork/
├── SKILL.md                        # Skill entry point (loaded by agent)
├── scripts/                        # Executable tool scripts
│   ├── fetch_jobs.py               #   Lark Hire API job fetcher (stdlib only)
│   ├── scrape_career.py            #   Playwright career page API interceptor
│   ├── browse_career.py            #   Career page explorer & API discovery
│   └── README.md                   #   Scripts usage guide
├── references/                     # Module detailed docs (loaded on demand)
│   ├── 01-resume-generator.md
│   ├── 02-company-explorer.md
│   ├── 03-campus-recruitment-finder.md
│   ├── 04-job-jd-fetcher.md
│   ├── 05-resume-job-matcher.md
│   ├── 06-gap-analyzer.md
│   ├── 07-interview-prep.md
│   └── 08-application-tracker.md
└── assets/
    ├── companies.json              # Company config template
    ├── company-database.md         # Local company database (Changsha IT/Security/BigTech)
    └── brag-doc-template.md        # Personal experience inventory template
```

## Design Principles

- **Progressive disclosure** — metadata (~100 tokens) → SKILL.md (<5000 tokens) → references/ (on demand)
- **Modular** — 8 modules work independently or as a pipeline
- **Scripts as black boxes** — called via CLI args, agents don't need to read source
- **Real data only** — all jobs/reviews must include source URLs, no fabrication
- **Brag doc driven** — fill once, reuse across resume generation and interview prep

## Acknowledgements

This project was inspired by the following open-source Agent Skill projects:

### Specification & Architecture

| Project | Description | What we learned |
|---------|-------------|-----------------|
| [anthropics/skills](https://github.com/anthropics/skills) | Anthropic's official Skill examples | Agent Skills spec, directory structure, progressive disclosure |
| [agentskills.io](https://agentskills.io/specification) | Agent Skills open specification | Frontmatter standard, scripts/references/assets conventions |

### Job Hunting Skills

| Project | ⭐ | Description | What we learned |
|---------|---|-------------|-----------------|
| [Paramchoudhary/ResumeSkills](https://github.com/Paramchoudhary/ResumeSkills) | 683 | 20 modular resume/career skills | Modular architecture, bullet writing, ATS optimization |
| [liyupi/yupi-skill](https://github.com/liyupi/yupi-skill) | 312 | Chinese developer knowledge distillation | Chinese job market, personal IP approach |
| [surapuramakhil-org/Job_search_agent](https://github.com/surapuramakhil-org/Job_search_agent) | 150 | Auto search + apply agent | Automation workflow design |
| [spontaneousai/job-hunt-copilot](https://github.com/spontaneousai/job-hunt-copilot) | 136 | Inventory + tailored resumes + interview scripts | Brag Doc mechanism |
| [couragec/LLMInternSkill](https://github.com/couragec/LLMInternSkill) | 113 | LLM internship job-search skill | Evidence Guard anti-fabrication |
| [SankaiAI/ats-optimized-resume-agent-skill](https://github.com/SankaiAI/ats-optimized-resume-agent-skill) | 71 | ATS-optimized resume skill | Gate system, humanization pass, JSON schema |
| [jason-huanghao/jobradar](https://github.com/jason-huanghao/jobradar) | 39 | Germany + China tech job search | Dual-market coverage |
| [Jichengyuuuuu/resume-builder-skill](https://github.com/Jichengyuuuuu/resume-builder-skill) | 31 | Chinese resume builder | Dynamic skill dimensions, HTML+DOCX output |
| [YIKUAIBANZI/job-hunter](https://github.com/YIKUAIBANZI/job-hunter) | 20 | Batch application automation | JD matching, application tracking |
| [earino/resumasher](https://github.com/earino/resumasher) | 7 | Resume + cover letter + interview prep | Interview prep module design |
| [REALGSY/offer-catcher](https://github.com/REALGSY/offer-catcher) | 2 | Campus recruitment matching agent | Campus recruitment reference |

Thanks to all the above projects for their contributions to the open-source ecosystem.

## License

MIT
