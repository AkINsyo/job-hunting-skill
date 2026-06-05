# scripts/ — 通用招聘工具脚本

本目录包含 3 个通用 Python 脚本，适用于所有使用飞书招聘 (Lark Hire) 系统的企业。

## 工具一览

| 脚本 | 用途 | 依赖 |
|------|------|------|
| `fetch_jobs.py` | 直接调用飞书招聘 API 拉取岗位 | 无（标准库） |
| `scrape_career.py` | Playwright 拦截校招页面 API | playwright |
| `browse_career.py` | 交互式浏览校招页面，发现 API | playwright |

## 快速开始

### 1. 已知 API 信息 → 直接拉取

```bash
python scripts/fetch_jobs.py \
  --company 安克创新 \
  --api-url "https://rainbow-recall.anker.com.cn/api/lark/hire/v1/jobs" \
  --website-id 6962795203808217351 \
  --city 长沙 --city-code CT_20 \
  --output jobs/anker_jobs.json \
  --markdown jobs/anker_jobs.md
```

### 2. 只知道校招页面 → 自动拦截

```bash
python scripts/scrape_career.py \
  --url "https://career.xxx.com/campus" \
  --click-text "投递岗位" \
  --output jobs/xxx_jobs.json
```

### 3. 什么都不知道 → 先探查

```bash
python scripts/browse_career.py \
  --base-url "https://career.xxx.com" \
  --explore --output api_report.json
```

### 4. 批量拉取

```bash
# 编辑 scripts/companies.json 添加公司
python scripts/fetch_jobs.py --config scripts/companies.json --output-dir jobs/
```

## 配置文件

`companies.json` 格式：

```json
[
  {
    "company": "公司名",
    "api_url": "飞书招聘 API URL",
    "website_id": "招聘网站 ID",
    "city_code": "城市代码（可选）",
    "city_name": "城市中文名（可选）",
    "max_pages": 20
  }
]
```

## 如何获取 websiteId

1. 用 `browse_career.py --base-url "..." --explore` 自动探查
2. 用 `scrape_career.py --url "..." --discover-only` 拦截 API
3. 浏览器 F12 → Network → 搜索 `websiteId`

## 飞书招聘 API 须知

- `page_size` 上限为 20（超过会返回错误 99992402）
- 分页通过 `page_token` + `has_more` 控制
- 城市过滤通过 `city_code`（如 CT_20 = 长沙）
- 常见 API 路径: `*/api/lark/hire/v1/jobs`
