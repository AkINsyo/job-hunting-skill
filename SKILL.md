---
name: seekmywork
description: AI 辅助求职 Skill 调度入口。包含简历生成、公司遍历筛选、校招查询、岗位拉取、简历匹配、差距分析 6 个子模块。Use when 用户说"求职""校招""找工作""完整流程"。
metadata:
  version: "3.0.0"
  tags: [求职, 校招, 实习, 简历, 岗位匹配, 公司调研]
  modules:
    - resume-generator
    - company-explorer
    - campus-recruitment-finder
    - job-jd-fetcher
    - resume-job-matcher
    - gap-analyzer
---

# SeekMyWork — AI 辅助求职 Skill

## Overview

SeekMyWork 是一个模块化的 AI 求职顾问系统，由 6 个可独立调用的子模块组成。用户可以触发单个模块，也可以组合执行完整流程。

**核心原则：你是顾问，不是决策者。呈现信息和分析，让用户自己判断。**

## 模块列表

| 模块 | Skill 名称 | 功能 | 独立可用 |
|------|-----------|------|---------|
| Module 1 | `resume-generator` | 采集信息 → 生成结构化简历 | ✅ |
| **Module 2** | **`company-explorer`** | **行业调研 → 公司筛选 → 员工评价 → 推荐清单** | **✅** |
| Module 3 | `campus-recruitment-finder` | 查找企业校招官网入口 | ✅ |
| Module 4 | `job-jd-fetcher` | 拉取岗位 JD 到本地 | ✅ |
| Module 5 | `resume-job-matcher` | 简历与岗位匹配打分 | 需 1+4 |
| Module 6 | `gap-analyzer` | 差距分析 & 提升计划 | 需 1+4 |

详细调用流程见 [FLOW.md](FLOW.md)。

## 通用脚本工具

`scripts/` 目录下提供 3 个通用 Python 脚本，适用于所有使用飞书招聘系统的企业：

| 脚本 | 用途 | 依赖 |
|------|------|------|
| `scripts/fetch_jobs.py` | 直接调用飞书招聘 API 拉取岗位 | 无 |
| `scripts/scrape_career.py` | Playwright 拦截校招页面 API | playwright |
| `scripts/browse_career.py` | 交互式浏览，发现 API 端点 | playwright |

详见 [scripts/README.md](scripts/README.md)。

## When to Use

### 适用场景
- ✅ 应届生/实习生找校招岗位
- ✅ 需要从零生成简历
- ✅ **不确定哪些公司值得投，需要行业调研**
- ✅ 想了解目标公司在招什么
- ✅ 想知道简历与岗位的匹配度
- ✅ 想获得针对性的提升建议

### 不适用场景
- ❌ 社招求职（本 Skill 聚焦校招/实习）
- ❌ 已有 offer 的薪资谈判
- ❌ 职业规划咨询（不做长期规划）

## 触发方式

### 独立触发

| 用户说 | 加载模块 |
|--------|---------|
| 帮我写简历 / 生成简历 | `resume-generator` |
| **帮我找公司 / 哪些公司适合我 / 筛选目标公司** | **`company-explorer`** |
| 找校招网站 / XX校招在哪 | `campus-recruitment-finder` |
| 看看在招什么 / 拉取岗位 | `job-jd-fetcher` |
| 帮我匹配 / 推荐岗位 | `resume-job-matcher` |
| 分析不足 / 提升建议 | `gap-analyzer` |

### 组合触发

| 用户说 | 执行流程 |
|--------|---------|
| 完整流程 / 从头开始 | 1 → 2 → 3 → 4 → 5 → 6 |
| 帮我匹配（无简历时） | 1 → 2 → 3 → 4 → 5 |
| 帮我找公司并匹配 | 2 → 3 → 4 → 5 |
| 看看在招什么并匹配 | 3 → 4 → 5 |

## 快速参考

### 输出文件

```
简历_{用户名}.md          ← Module 1
目标公司清单_{日期}.md    ← Module 2
校招网站汇总.md           ← Module 3
jobs/{公司}_岗位.json/.md  ← Module 4
匹配结果_{日期}.md         ← Module 5
提升计划_{日期}.md         ← Module 6
```

### 关键规则

1. **一次只问一个问题** — 不要列出清单轰炸用户
2. **所有岗位必须附原始链接** — 不编造、不猜测
3. **员工评价必须注明来源** — 不编造口碑数据
4. **只推荐免费资源** — 不建议付费课程/服务
5. **不替用户做决定** — 用"建议""推荐"而非"你应该"
6. **不做价值评判** — 不评价学校/学历好坏

## Common Rationalizations

| 借口 | 现实 | 应对 |
|------|------|------|
| "用户只要结果，跳过确认" | 跳过确认可能跑偏 | 至少让用户确认一次 |
| "搜不到就算了" | 搜不到也要告知原因 | 如实说明搜索情况 |
| "差不多就行了" | 差不多 ≠ 够好 | 每个步骤都要验证 |
| "用户指定了公司，跳过调研" | 指定公司也需要了解口碑 | 对指定公司也做评价调研 |

## Verification

完整流程结束后确认：
- [ ] 简历已生成且用户确认
- [ ] **目标公司清单已输出且用户确认**
- [ ] 校招网站已验证可访问
- [ ] 岗位 JD 已保存且有原始链接
- [ ] 匹配结果有具体维度分析
- [ ] 提升计划有可执行的行动项
- [ ] 所有文件路径已告知用户
