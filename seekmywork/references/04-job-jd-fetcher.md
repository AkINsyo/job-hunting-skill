# 企业招聘岗位查询 & JD 拉取

## Overview

从企业校招页面或招聘平台搜索具体岗位，拉取 JD（职位描述）并提取为结构化数据，保存为 JSON + Markdown 双格式到本地。

**核心工具**：`scripts/` 目录下提供 3 个通用 Python 脚本，适用于所有使用飞书招聘系统的企业。

## 通用脚本

| 脚本 | 用途 | 适用场景 |
|------|------|---------|
| `scripts/browse_career.py` | 浏览校招页面，发现 API 端点 | 不知道 websiteId 时，先用这个探查 |
| `scripts/scrape_career.py` | Playwright 拦截 API，提取岗位 | 已知校招页面 URL，自动抓取 |
| `scripts/fetch_jobs.py` | 直接调用飞书招聘 API 拉取 | 已知 API URL 和 websiteId |

### 典型工作流

```
Step 1: 发现 API
  browse_career.py --base-url "https://career.xxx.com" --explore
  → 找到 API URL + websiteId

Step 2: 拉取岗位
  fetch_jobs.py --api-url "..." --website-id XXX --city 长沙
  → 生成 jobs/xxx_jobs.json + .md

  或者用 scrape_career.py 一步到位:
  scrape_career.py --url "https://career.xxx.com/campus" --click-text "投递岗位"
```

### fetch_jobs.py 详解

直接调用飞书招聘 (Lark Hire) API，自动处理分页。

```bash
# 单公司拉取
python scripts/fetch_jobs.py \
  --company 安克创新 \
  --api-url "https://rainbow-recall.anker.com.cn/api/lark/hire/v1/jobs" \
  --website-id 6962795203808217351 \
  --city 长沙 --city-code CT_20 \
  --output jobs/anker_jobs.json \
  --markdown jobs/anker_jobs.md

# 批量拉取（从配置文件）
python scripts/fetch_jobs.py --config scripts/companies.json --output-dir jobs/
```

**参数说明**：

| 参数 | 说明 | 必填 |
|------|------|------|
| `--api-url` | 飞书招聘 API URL | 单公司模式必填 |
| `--website-id` | 招聘网站 ID | 单公司模式必填 |
| `--city` | 城市中文名（二次过滤） | 选填 |
| `--city-code` | 城市代码（如 CT_20） | 选填 |
| `--output` | 输出 JSON 路径 | 选填 |
| `--markdown` | 输出 Markdown 路径 | 选填 |
| `--config` | 公司配置文件 | 批量模式必填 |
| `--output-dir` | 批量输出目录 | 选填，默认 jobs/ |

### scrape_career.py 详解

用 Playwright 打开校招页面，拦截 XHR 请求，自动解析岗位数据。

```bash
# 基本用法
python scripts/scrape_career.py \
  --url "https://career.xxx.com/campus" \
  --click-text "投递岗位" \
  --output jobs/xxx_api.json \
  --markdown jobs/xxx_jobs.md

# 仅发现 API
python scripts/scrape_career.py --url "https://career.xxx.com/campus" --discover-only
```

### browse_career.py 详解

交互式浏览校招页面，发现 API 端点和 websiteId。

```bash
# 探索模式：自动尝试多种 URL
python scripts/browse_career.py --base-url "https://career.xxx.com" --explore

# 指定页面 + 列出可点击元素
python scripts/browse_career.py --url "https://career.xxx.com/campus" --list-links

# 交互模式：按顺序点击
python scripts/browse_career.py \
  --url "https://career.xxx.com/campus" \
  --click-sequence "校园招聘,投递岗位" \
  --output api_report.json
```

## When to Use

### 适用场景
- ✅ 用户想看某公司在招哪些岗位
- ✅ 用户想拉取特定方向的岗位 JD
- ✅ 需要发现企业招聘 API 端点
- ✅ Module 4 需要岗位数据作为输入

### 不适用场景
- ❌ 用户只需要校招网站链接（→ campus-recruitment-finder）
- ❌ 用户想找社招岗位（本模块聚焦校招/实习）

## Core Process

### Phase 1: 获取输入

需要以下信息（从用户获取或从上游模块继承）：

| 信息 | 必填 | 来源 |
|------|------|------|
| 公司名 | ✅ | 用户指定 |
| 校招页面 URL | 选填 | campus-recruitment-finder 产出 |
| API URL + websiteId | 选填 | browse_career.py 发现 |
| 岗位方向 | 选填 | 用户指定（如"后端开发"） |
| 城市 | 选填 | 用户指定，默认不限 |

### Phase 2: 确定拉取方式

按优先级选择：

1. **已有 API 信息**（API URL + websiteId）→ 直接用 `fetch_jobs.py`
2. **有校招页面 URL** → 用 `scrape_career.py` 拦截
3. **只有公司名** → 先用 `browse_career.py --explore` 发现，再拉取
4. **都没有** → 用 `web_search` 搜索校招页面，再走 2 或 3

### Phase 3: 拉取岗位

使用对应脚本拉取，详见上方脚本说明。

### Phase 4: 提取结构化 JD

从拉取的数据中提取标准化字段：

```json
{
  "company": "公司全称",
  "position": "岗位名称",
  "city": "工作地点",
  "education": "学历要求",
  "skills": ["技能1", "技能2"],
  "responsibilities": ["职责1", "职责2"],
  "bonuses": ["加分项1", "加分项2"],
  "deadline": "截止日期",
  "source_url": "原始链接"
}
```

### Phase 5: 保存到本地

**目录结构**：
```
jobs/
  {公司名}_jobs.json       ← 结构化数据
  {公司名}_jobs.md         ← 人类可读版
```

### Phase 6: 输出汇总

向用户展示：
- 共拉取了多少个岗位
- 按方向/城市分类统计
- 文件保存位置

## 公司配置文件

`scripts/companies.json` 格式：

```json
[
  {
    "company": "安克创新",
    "api_url": "https://rainbow-recall.anker.com.cn/api/lark/hire/v1/jobs",
    "website_id": "6962795203808217351",
    "city_code": "CT_20",
    "city_name": "长沙",
    "max_pages": 20
  }
]
```

**如何获取 websiteId**：
1. 用 `browse_career.py --explore` 探查
2. 用 `scrape_career.py --discover-only` 拦截
3. 浏览器 F12 → Network → 搜索 `websiteId`

## Rules

### 必须遵守
- ✅ 所有岗位必须附原始链接（source_url）
- ✅ 保存 JSON + Markdown 双格式
- ✅ 每个岗位的 skills 字段从 JD 原文提取，不要泛化
- ✅ 多家公司时，为每家生成独立文件

### 禁止事项
- ❌ 编造任何岗位信息
- ❌ 搜索不足时凑数填入不相关岗位
- ❌ 省略 source_url 字段

## Common Rationalizations

| 借口 | 现实 | 应对 |
|------|------|------|
| "搜到的信息差不多了" | 差不多 ≠ 充分 | 至少覆盖 3 个查询词 |
| "JD 太长，摘要一下就行" | 摘要会丢失细节 | 保留完整 skills 和 responsibilities |
| "这个链接打不开，跳过吧" | 可能是临时问题 | 重试一次，仍失败则标注 |
| "脚本跑不了，手动编一个" | 手动编造 ≠ 真实数据 | 报告工具故障，建议用户手动访问 |

## Red Flags

- 🚩 搜索结果全是第三方转载：尝试直接访问校招官网
- 🚩 JD 内容与岗位名称不符：可能是挂羊头卖狗肉，标注后告知用户
- 🚩 用户指定的公司搜不到校招信息：如实告知，建议确认公司是否有校招
- 🚩 API 返回 page_size 错误（99992402）：飞书招聘 page_size 上限为 20

## Verification

完成后确认：
- [ ] 每个岗位均有 source_url
- [ ] JSON 文件格式正确可解析
- [ ] Markdown 文件人类可读
- [ ] 文件已保存到 jobs/ 目录
- [ ] 告知用户文件位置