#!/usr/bin/env python3
"""
scrape_career.py — 通用校招页面 API 拦截工具

用 Playwright 打开任意企业校招/招聘页面，拦截所有 XHR/Fetch 请求，
自动识别并解析岗位 API（飞书招聘、北森等），输出结构化岗位数据。

适用于：发现企业招聘 API 端点 + 拉取初始岗位数据。

Usage:
    # 基本用法：拦截 API 并保存
    python scripts/scrape_career.py --url "https://career.xxx.com/campus" --output jobs/xxx_api.json

    # 指定过滤关键词
    python scripts/scrape_career.py --url "https://career.xxx.com/campus" \\
        --filter-keywords api,job,position,recruit,hire

    # 等待更长时间（慢加载页面）
    python scripts/scrape_career.py --url "https://career.xxx.com/campus" --wait 10

    # 点击特定按钮后再拦截
    python scripts/scrape_career.py --url "https://career.xxx.com/campus" \\
        --click-text "投递岗位" --wait 8

    # 非 headless 模式（调试用）
    python scripts/scrape_career.py --url "https://career.xxx.com/campus" --no-headless

    # 仅发现 API 端点，不解析数据
    python scripts/scrape_career.py --url "https://career.xxx.com/campus" --discover-only
"""
import argparse
import json
import sys
import re
from pathlib import Path
from datetime import datetime

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Error: playwright not installed. Run: pip install playwright && playwright install chromium")
    sys.exit(1)


# ── 常见招聘 API 路径模式 ─────────────────────────────────────
API_PATTERNS = [
    r"api.*job",
    r"api.*position",
    r"api.*recruit",
    r"api.*hire",
    r"api.*career",
    r"api.*campus",
    r"api.*lark/hire",
    r"api.*v1/jobs",
    r"api.*opening",
    r"api.*vacancy",
]

# ── 常见招聘平台域名标识 ──────────────────────────────────────
PLATFORM_IDENTIFIERS = {
    "feishu": ["feishu.cn", "lark.", "bytedance.net"],
    "beisen": ["beisen", "bt.3.cn"],
    "liepin": ["liepin"],
    "zhaopin": ["zhaopin", "51job"],
    "moka": ["moka.", "mokahr"],
    "custom": [],  # 企业自建
}


def identify_platform(url: str) -> str:
    """根据 URL 识别招聘平台。"""
    url_lower = url.lower()
    for platform, markers in PLATFORM_IDENTIFIERS.items():
        for marker in markers:
            if marker in url_lower:
                return platform
    return "custom"


def matches_api_pattern(url: str, keywords: list[str] = None) -> bool:
    """判断 URL 是否匹配已知招聘 API 模式。"""
    url_lower = url.lower()

    # 用户自定义关键词
    if keywords:
        return any(kw.lower() in url_lower for kw in keywords)

    # 自动匹配
    return any(re.search(p, url_lower, re.IGNORECASE) for p in API_PATTERNS)


def try_parse_json(text: str) -> dict | None:
    """尝试解析 JSON，失败返回 None。"""
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None


def extract_lark_jobs(data: dict) -> list[dict]:
    """从飞书招聘 API 响应中提取岗位列表。"""
    if not isinstance(data, dict):
        return []

    # 标准飞书招聘格式
    if data.get("code") == 0 and "data" in data:
        items = data["data"].get("items", [])
        jobs = []
        for item in items:
            jobs.append({
                "title": item.get("title", ""),
                "city": item.get("city", {}).get("zh_name", ""),
                "function": item.get("job_function", {}).get("name", {}).get("zh_cn", ""),
                "type": item.get("recruitment_type", {}).get("zh_name", ""),
                "dept": item.get("department", {}).get("zh_name", ""),
                "code": item.get("code", ""),
                "id": item.get("id", ""),
                "desc": (item.get("description") or "")[:2000],
                "requirement": (item.get("requirement") or "")[:2000],
            })
        return jobs

    # 尝试通用 JSON 结构
    if "data" in data:
        inner = data["data"]
        if isinstance(inner, list):
            return inner
        if isinstance(inner, dict):
            for key in ["items", "list", "records", "jobs", "positions"]:
                if key in inner and isinstance(inner[key], list):
                    return inner[key]

    return []


def extract_generic_jobs(data: dict | list) -> list[dict]:
    """通用岗位提取：尝试从任意 JSON 中找到岗位列表。"""
    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        # 递归搜索含有 title/position/name + city/location 字段的列表
        for key in ["data", "items", "list", "records", "jobs", "positions", "result"]:
            if key in data:
                val = data[key]
                if isinstance(val, list) and val:
                    # 检查第一个元素是否像岗位数据
                    first = val[0]
                    if isinstance(first, dict):
                        has_title = any(
                            k in first for k in ["title", "position", "name", "jobTitle"]
                        )
                        if has_title:
                            return val
                elif isinstance(val, dict):
                    result = extract_generic_jobs(val)
                    if result:
                        return result
    return []


def scrape_career_page(
    url: str,
    filter_keywords: list[str] = None,
    click_text: str = None,
    wait_seconds: int = 5,
    headless: bool = True,
    discover_only: bool = False,
    screenshot_path: str = None,
) -> dict:
    """
    打开校招页面，拦截 API 请求，返回发现的 API 和岗位数据。

    Returns:
        {
            "url": 原始 URL,
            "platform": 识别的平台,
            "apis": [{"url": ..., "status": ..., "content_type": ..., "jobs_count": ...}],
            "jobs": [提取的岗位列表],
            "page_title": 页面标题,
            "page_text_preview": 页面文本前 500 字,
        }
    """
    result = {
        "url": url,
        "platform": identify_platform(url),
        "apis": [],
        "jobs": [],
        "page_title": "",
        "page_text_preview": "",
    }

    intercepted = []

    def on_response(response):
        resp_url = response.url
        # 过滤静态资源
        skip_exts = (".css", ".js", ".png", ".jpg", ".gif", ".svg", ".woff", ".ico", ".map")
        if any(resp_url.lower().endswith(ext) for ext in skip_exts):
            return

        if matches_api_pattern(resp_url, filter_keywords):
            content_type = ""
            try:
                content_type = response.headers.get("content-type", "")
            except:
                pass

            body_text = ""
            status = response.status
            try:
                body_text = response.text()
            except:
                pass

            intercepted.append({
                "url": resp_url,
                "status": status,
                "content_type": content_type,
                "body": body_text[:10000],  # 限制大小
            })

    print(f"Opening: {url}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        page.on("response", on_response)

        try:
            page.goto(url, timeout=30000)
            page.wait_for_timeout(wait_seconds * 1000)

            result["page_title"] = page.title()
            try:
                body_text = page.inner_text("body")
                result["page_text_preview"] = body_text[:500]
            except:
                pass

            # 点击按钮
            if click_text:
                print(f"Looking for element with text: '{click_text}'")
                links = page.query_selector_all("a, button")
                for link in links:
                    text = link.inner_text().strip()
                    if click_text in text:
                        print(f"Clicking: [{text}]")
                        link.click()
                        page.wait_for_timeout(wait_seconds * 1000)
                        break

            # 截图
            if screenshot_path:
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"Screenshot saved → {screenshot_path}")

        except Exception as e:
            print(f"Page error: {e}")
        finally:
            browser.close()

    # 处理拦截到的 API
    print(f"\nIntercepted {len(intercepted)} API responses")

    for api_resp in intercepted:
        api_info = {
            "url": api_resp["url"],
            "status": api_resp["status"],
            "content_type": api_resp["content_type"],
            "jobs_count": 0,
        }

        if api_resp["body"]:
            data = try_parse_json(api_resp["body"])
            if data:
                # 飞书招聘
                jobs = extract_lark_jobs(data)
                if not jobs:
                    jobs = extract_generic_jobs(data)

                api_info["jobs_count"] = len(jobs)

                if not discover_only:
                    result["jobs"].extend(jobs)

                print(f"  API: {api_resp['url'][:100]}")
                print(f"    Status: {api_resp['status']} | Jobs: {len(jobs)}")

        result["apis"].append(api_info)

    # 去重
    if not discover_only and result["jobs"]:
        seen = set()
        unique_jobs = []
        for job in result["jobs"]:
            key = job.get("code") or job.get("id") or job.get("title", "")
            if key and key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        result["jobs"] = unique_jobs

    return result


def save_results(result: dict, output_path: str, markdown_path: str = None):
    """保存结果到文件。"""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\nSaved → {output_path}")

    if markdown_path and result["jobs"]:
        lines = [
            f"# 校招岗位汇总\n",
            f"> 来源：{result['url']}",
            f"> 平台：{result['platform']}",
            f"> 时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"> 岗位数：{len(result['jobs'])}",
            "",
        ]
        for i, job in enumerate(result["jobs"], 1):
            title = job.get("title") or job.get("name") or f"岗位 {i}"
            lines.append(f"## {i}. {title}")
            for field in ["city", "function", "type", "dept", "code"]:
                if job.get(field):
                    label = {"function": "分类", "type": "类型", "dept": "部门", "code": "编号"}.get(field, field)
                    lines.append(f"- **{label}**：{job[field]}")
            if job.get("desc"):
                lines.append(f"\n### 描述\n\n{job['desc']}")
            if job.get("requirement"):
                lines.append(f"\n### 要求\n\n{job['requirement']}")
            lines.append("")

        with open(markdown_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"Saved Markdown → {markdown_path}")


def main():
    parser = argparse.ArgumentParser(
        description="通用校招页面 API 拦截工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 安克创新校招
  python scripts/scrape_career.py \\
    --url "https://career.anker.com.cn/universities/recruitment" \\
    --click-text "投递岗位" --output jobs/anker_api.json

  # 发现 API 端点
  python scripts/scrape_career.py \\
    --url "https://hr.xiaomi.com/campus" \\
    --discover-only
        """,
    )

    parser.add_argument("--url", "-u", required=True, help="校招页面 URL")
    parser.add_argument("--filter-keywords", "-k", default="",
                        help="API 过滤关键词（逗号分隔），默认自动匹配")
    parser.add_argument("--click-text", "-c", help="页面加载后点击的按钮文本")
    parser.add_argument("--wait", "-w", type=int, default=5, help="页面加载等待秒数")
    parser.add_argument("--no-headless", action="store_true", help="显示浏览器窗口")
    parser.add_argument("--discover-only", action="store_true", help="仅发现 API 端点")
    parser.add_argument("--output", "-o", help="输出 JSON 路径")
    parser.add_argument("--markdown", "-m", help="输出 Markdown 路径")
    parser.add_argument("--screenshot", "-s", help="截图保存路径")

    args = parser.parse_args()

    keywords = [k.strip() for k in args.filter_keywords.split(",") if k.strip()] if args.filter_keywords else None

    result = scrape_career_page(
        url=args.url,
        filter_keywords=keywords,
        click_text=args.click_text,
        wait_seconds=args.wait,
        headless=not args.no_headless,
        discover_only=args.discover_only,
        screenshot_path=args.screenshot,
    )

    # 输出摘要
    print(f"\n{'='*60}")
    print(f"Platform: {result['platform']}")
    print(f"APIs found: {len(result['apis'])}")
    for api in result["apis"]:
        print(f"  [{api['status']}] {api['url'][:80]}  → {api['jobs_count']} jobs")
    print(f"Total jobs extracted: {len(result['jobs'])}")

    # 保存
    if args.output:
        save_results(result, args.output, args.markdown)
    else:
        # 默认输出到 stdout
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
