# Changelog

## v5.0.0 (2026-06-05)

### New Modules

- **Module 7: Interview Prep** — 面试题预测、技术知识点清单、STAR 回答框架、反问建议
- **Module 8: Application Tracker** — 投递状态记录、进度汇总、待办提醒
- **Brag Doc Template** — `assets/brag-doc-template.md`，个人经历素材库模板

### Improvements

- Resume Generator: 新增 Stage 0（素材库检查）、Evidence Guard（反编造守卫）、素材库同步回写
- Resume Generator: JD 分析、ATS 优化、人性化检查、JSON 结构化输出
- SKILL.md: 升级至 v5.0.0，8 模块决策树

### Inspiration

- [Paramchoudhary/ResumeSkills](https://github.com/Paramchoudhary/ResumeSkills) ⭐683 — 模块化架构
- [spontaneousai/job-hunt-copilot](https://github.com/spontaneousai/job-hunt-copilot) ⭐136 — 素材库机制
- [couragec/LLMInternSkill](https://github.com/couragec/LLMInternSkill) ⭐113 — Evidence Guard
- [surapuramakhil-org/Job_search_agent](https://github.com/surapuramakhil-org/Job_search_agent) ⭐150 — 自动化搜索
- [SankaiAI/ats-optimized-resume-agent-skill](https://github.com/SankaiAI/ats-optimized-resume-agent-skill) ⭐71 — Gate 门控、反 AI 腔
- [Jichengyuuuuu/resume-builder-skill](https://github.com/Jichengyuuuuu/resume-builder-skill) ⭐31 — 按岗位动态维度
- [earino/resumasher](https://github.com/earino/resumasher) ⭐7 — 面试准备包
- [YIKUAIBANZI/job-hunter](https://github.com/YIKUAIBANZI/job-hunter) ⭐20 — 批量投递追踪

---

## v4.0.0 (2026-06-05)

### Restructure

- Restructured to follow [Agent Skills specification](https://agentskills.io/specification)
- New layout: `seekmywork/SKILL.md` + `scripts/` + `references/` + `assets/`
- Frontmatter: `name` + `description` (required), `compatibility` + `metadata` (optional)
- SKILL.md under 500 lines, progressive disclosure pattern

### New Scripts

- `scripts/fetch_jobs.py` — Generic Lark Hire API job fetcher (CLI, stdlib only)
- `scripts/scrape_career.py` — Playwright career page API interceptor
- `scripts/browse_career.py` — Career page explorer & API discovery

### Inspiration

- [anthropics/skills](https://github.com/anthropics/skills) — Agent Skills reference implementation
- [agentskills.io](https://agentskills.io/specification) — Agent Skills specification

---

## v3.0.0 (2026-06-05)

### Initial

- 6-module pipeline: resume → company → campus → jobs → match → gap
- Anker-specific Python scripts (hardcoded)
- Monolithic SKILL.md with sub-skill directories
