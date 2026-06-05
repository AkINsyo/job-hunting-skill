#!/usr/bin/env python3
"""
fetch_jobs.py — 通用飞书招聘 (Lark Hire) API 岗位拉取工具

适用于所有使用飞书招聘系统的企业校招/社招页面。
自动处理分页、城市过滤、字段提取，输出标准 JSON。

Usage:
    python scripts/fetch_jobs.py --api-url "https://xxx.com/api/lark/hire/v1/jobs" \
        --website-id 123456 --city 长沙 --output jobs/company_changsha.json

    python scripts/fetch_jobs.py --api-url "https://xxx.com/api/lark/hire/v1/jobs" \
        --website-id 123456 --city-code CT_20 --output jobs/company_changsha.json

    # 从配置文件批量拉取
    python scripts/fetch_jobs.py --config scripts/companies.json --output-dir jobs/
"""
import argparse
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime


# ── 默认字段映射 ──────────────────────────────────────────────
# 飞书招聘 API 返回的字段名 → 我们标准化的字段名
FIELD_MAP = {
    "title": "title",
    "city": "city",
    "job_function": "function",
    "recruitment_type": "type",
    "department": "dept",
    "subject": "subject",
    "description": "desc",
    "requirement": "requirement",
    "code": "code",
    "id": "id",
}


def extract_nested(obj, *keys):
    """从嵌套 dict 中提取值，支持 dict.name.zh_cn / dict.zh_name 等模式。"""
    for key in keys:
        if isinstance(obj, dict):
            obj = obj.get(key, "")
        else:
            return ""
    return obj if isinstance(obj, str) else ""


def extract_job(job: dict) -> dict:
    """从单个岗位原始数据中提取标准化字段。"""
    city = job.get("city", {})
    city_name = city.get("zh_name", "") if isinstance(city, dict) else ""
    if not city_name:
        city_list = job.get("city_list", [])
        city_name = ", ".join(
            c.get("name", {}).get("zh_cn", "")
            for c in city_list
            if c.get("name", {}).get("zh_cn")
        )

    return {
        "title": job.get("title", ""),
        "city": city_name,
        "function": extract_nested(job, "job_function", "name", "zh_cn"),
        "type": extract_nested(job, "recruitment_type", "zh_name"),
        "dept": extract_nested(job, "department", "zh_name"),
        "subject": extract_nested(job, "subject", "name", "zh_cn"),
        "desc": (job.get("description") or "")[:2000],
        "requirement": (job.get("requirement") or "")[:2000],
        "code": job.get("code", ""),
        "id": job.get("id", ""),
    }


def fetch_page(api_url: str, website_id: str, page_token: str = "",
               city_code: str = "", extra_params: dict = None) -> dict:
    """请求单页数据。返回原始 JSON dict。"""
    params = {
        "page_size": "20",
        "websiteId": website_id,
    }
    if city_code:
        params["city_code"] = city_code
    if page_token:
        params["page_token"] = page_token
    if extra_params:
        params.update(extra_params)

    query = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"{api_url}?{query}"

    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"code": -1, "msg": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        return {"code": -1, "msg": str(e)}


def fetch_all_jobs(api_url: str, website_id: str, city_code: str = "",
                   city_name: str = "", max_pages: int = 20,
                   extra_params: dict = None) -> list[dict]:
    """
    拉取所有岗位（自动分页）。

    Args:
        api_url:       飞书招聘 API 基础 URL
        website_id:    招聘网站 ID
        city_code:     城市代码（如 CT_20），可选
        city_name:     城市中文名（用于二次过滤），可选
        max_pages:     最大翻页数
        extra_params:  额外请求参数

    Returns:
        提取后的岗位列表
    """
    all_jobs = []
    page_token = ""
    page = 0

    while page < max_pages:
        page += 1
        print(f"  Fetching page {page}...", end="", flush=True)

        data = fetch_page(api_url, website_id, page_token, city_code, extra_params)

        if data.get("code") != 0:
            print(f" Error: {data.get('msg', 'unknown')}")
            break

        items = data.get("data", {}).get("items", [])
        if not items:
            print(" empty page, done.")
            break

        # 提取并过滤
        for job in items:
            extracted = extract_job(job)
            if city_name and city_name not in extracted["city"]:
                continue
            all_jobs.append(extracted)

        print(f" got {len(items)} items, total {len(all_jobs)}")

        # 翻页
        page_token = data.get("data", {}).get("page_token", "")
        has_more = data.get("data", {}).get("has_more", False)
        if not page_token or not has_more:
            break

    return all_jobs


def save_jobs(jobs: list[dict], output_path: str, company: str = ""):
    """保存岗位列表到 JSON 文件。"""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    print(f"\nSaved {len(jobs)} jobs → {output_path}")


def generate_markdown(jobs: list[dict], company: str, source_url: str = "") -> str:
    """生成人类可读的 Markdown 岗位汇总。"""
    lines = [
        f"# {company} — 校招岗位汇总\n",
        f"> 拉取时间：{datetime.now().strftime('%Y-%m-%d')}",
    ]
    if source_url:
        lines.append(f"> 数据来源：{source_url}")
    lines.append("")

    for i, job in enumerate(jobs, 1):
        lines.append(f"## {i}. {job['title']}")
        lines.append("")
        if job.get("city"):
            lines.append(f"- **城市**：{job['city']}")
        if job.get("type"):
            lines.append(f"- **类型**：{job['type']}")
        if job.get("function"):
            lines.append(f"- **分类**：{job['function']}")
        if job.get("dept"):
            lines.append(f"- **部门**：{job['dept']}")
        if job.get("subject"):
            lines.append(f"- **方向**：{job['subject']}")
        if job.get("code"):
            lines.append(f"- **编号**：{job['code']}")
        if job.get("desc"):
            lines.append(f"\n### 岗位描述\n\n{job['desc']}")
        if job.get("requirement"):
            lines.append(f"\n### 岗位要求\n\n{job['requirement']}")
        lines.append("")

    return "\n".join(lines)


def load_config(config_path: str) -> list[dict]:
    """
    从配置文件加载公司列表。

    配置文件格式 (JSON):
    [
      {
        "company": "安克创新",
        "api_url": "https://rainbow-recall.anker.com.cn/api/lark/hire/v1/jobs",
        "website_id": "6962795203808217351",
        "city_code": "CT_20",
        "city_name": "长沙"
      }
    ]
    """
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(
        description="通用飞书招聘 API 岗位拉取工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 单公司拉取
  python scripts/fetch_jobs.py \\
    --company 安克创新 \\
    --api-url "https://rainbow-recall.anker.com.cn/api/lark/hire/v1/jobs" \\
    --website-id 6962795203808217351 \\
    --city 长沙 --city-code CT_20

  # 从配置文件批量拉取
  python scripts/fetch_jobs.py --config scripts/companies.json --output-dir jobs/
        """,
    )

    # 单公司模式
    parser.add_argument("--company", help="公司名称")
    parser.add_argument("--api-url", help="飞书招聘 API URL")
    parser.add_argument("--website-id", help="招聘网站 ID")
    parser.add_argument("--city", help="城市中文名（用于二次过滤）")
    parser.add_argument("--city-code", default="", help="城市代码（如 CT_20）")
    parser.add_argument("--max-pages", type=int, default=20, help="最大翻页数")
    parser.add_argument("--output", "-o", help="输出 JSON 文件路径")
    parser.add_argument("--markdown", "-m", help="同时输出 Markdown 文件路径")

    # 批量模式
    parser.add_argument("--config", help="公司配置文件路径（JSON）")
    parser.add_argument("--output-dir", default="jobs/", help="批量输出目录")

    args = parser.parse_args()

    # ── 批量模式 ──
    if args.config:
        companies = load_config(args.config)
        print(f"Loaded {len(companies)} companies from {args.config}\n")
        for comp in companies:
            company = comp["company"]
            print(f"=== {company} ===")
            jobs = fetch_all_jobs(
                api_url=comp["api_url"],
                website_id=comp["website_id"],
                city_code=comp.get("city_code", ""),
                city_name=comp.get("city_name", ""),
                max_pages=comp.get("max_pages", 20),
            )
            if jobs:
                safe_name = company.replace("/", "_").replace(" ", "_")
                out_json = Path(args.output_dir) / f"{safe_name}_jobs.json"
                save_jobs(jobs, str(out_json), company)

                out_md = Path(args.output_dir) / f"{safe_name}_jobs.md"
                md = generate_markdown(jobs, company, comp.get("api_url", ""))
                with open(out_md, "w", encoding="utf-8") as f:
                    f.write(md)
                print(f"Saved Markdown → {out_md}")
            print()
        return

    # ── 单公司模式 ──
    if not args.api_url or not args.website_id:
        parser.error("单公司模式需要 --api-url 和 --website-id")

    company = args.company or "unknown"
    print(f"Fetching jobs for: {company}")
    if args.city:
        print(f"City filter: {args.city} ({args.city_code or 'by name'})")

    jobs = fetch_all_jobs(
        api_url=args.api_url,
        website_id=args.website_id,
        city_code=args.city_code,
        city_name=args.city or "",
        max_pages=args.max_pages,
    )

    if not jobs:
        print("\nNo jobs found.")
        sys.exit(1)

    # 输出
    output = args.output or f"jobs/{company}_jobs.json"
    save_jobs(jobs, output, company)

    if args.markdown:
        md = generate_markdown(jobs, company, args.api_url)
        with open(args.markdown, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"Saved Markdown → {args.markdown}")

    # 打印摘要
    print(f"\n{'='*50}")
    print(f"Total: {len(jobs)} jobs")
    cities = {}
    for j in jobs:
        c = j.get("city", "未知")
        cities[c] = cities.get(c, 0) + 1
    for c, n in sorted(cities.items(), key=lambda x: -x[1]):
        print(f"  {c}: {n}")


if __name__ == "__main__":
    main()
