#!/usr/bin/env python3
"""
browse_career.py — 通用校招页面浏览 & API 发现工具

交互式浏览企业校招页面，通过点击导航、切换标签页等操作，
发现并记录招聘 API 端点、website_id、page_size 限制等关键信息。

输出一份「API 发现报告」，可直接用于 fetch_jobs.py。

Usage:
    # 自动探索模式：尝试多种 URL 模式
    python scripts/browse_career.py --base-url "https://career.xxx.com" --explore

    # 指定页面 + 交互
    python scripts/browse_career.py --url "https://career.xxx.com/campus" \\
        --click-sequence "校园招聘,投递岗位" --output api_report.json

    # 列出所有可点击元素
    python scripts/browse_career.py --url "https://career.xxx.com/campus" --list-links

    # 调试模式（非 headless）
    python scripts/browse_career.py --url "https://career.xxx.com/campus" --no-headless --pause
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


# ── 常见校招 URL 模式 ─────────────────────────────────────────
CAREER_URL_PATTERNS = [
    "{base}/campus",
    "{base}/campus/jobs",
    "{base}/campus/job-list",
    "{base}/campus/recruitment",
    "{base}/universities/recruitment",
    "{base}/universities/recruitment/job-table",
    "{base}/universities/job-table",
    "{base}/campus/positions",
    "{base}/jobs",
    "{base}/job",
    "{base}/positions",
    "{base}/recruit/campus",
    "{base}/campushire",
    "{base}/graduate",
    "{base}/join/campus",
    "{base}/join/graduate",
]

# ── API 特征模式 ──────────────────────────────────────────────
API_SIGNATURES = {
    "lark_hire": {
        "patterns": [r"api/lark/hire", r"websiteId="],
        "description": "飞书招聘 (Lark Hire)",
        "extract_fields": ["websiteId", "page_size", "page_token"],
    },
    "beisen": {
        "patterns": [r"bt\.3\.cn", r"beisen", r"PositionAPI"],
        "description": "北森招聘",
        "extract_fields": [],
    },
    "moka": {
        "patterns": [r"mokahr", r"moka\."],
        "description": "Moka 招聘",
        "extract_fields": [],
    },
    "generic_api": {
        "patterns": [r"api.*job", r"api.*position", r"api.*recruit"],
        "description": "通用招聘 API",
        "extract_fields": [],
    },
}


def identify_api_type(url: str) -> str | None:
    """识别 API 类型。"""
    for api_type, config in API_SIGNATURES.items():
        for pattern in config["patterns"]:
            if re.search(pattern, url, re.IGNORECASE):
                return api_type
    return None


def extract_website_id(url: str) -> str | None:
    """从 URL 中提取 websiteId。"""
    match = re.search(r"websiteId[=:](\d+)", url)
    return match.group(1) if match else None


def extract_page_size(url: str) -> int | None:
    """从 URL 中提取 page_size。"""
    match = re.search(r"page_size[=:](\d+)", url)
    return int(match.group(1)) if match else None


def normalize_url(base: str, path: str) -> str:
    """拼接 base URL 和 path。"""
    base = base.rstrip("/")
    path = path.lstrip("/")
    return f"{base}/{path}"


class CareerBrowser:
    """校招页面浏览器，支持 API 发现和交互。"""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.apis_found = []
        self.pages_visited = []

    def _on_response(self, response):
        url = response.url
        # 过滤静态资源
        skip_exts = (".css", ".js", ".png", ".jpg", ".gif", ".svg", ".woff", ".ico", ".map")
        if any(url.lower().endswith(ext) for ext in skip_exts):
            return

        api_type = identify_api_type(url)
        if api_type:
            website_id = extract_website_id(url)
            page_size = extract_page_size(url)
            content_type = ""
            status = response.status
            body_preview = ""
            try:
                content_type = response.headers.get("content-type", "")
                body_preview = response.text()[:500]
            except:
                pass

            self.apis_found.append({
                "url": url,
                "type": api_type,
                "status": status,
                "content_type": content_type,
                "website_id": website_id,
                "page_size": page_size,
                "body_preview": body_preview,
            })

    def visit_page(self, page, url: str, wait: int = 3) -> dict:
        """访问一个页面并返回基本信息。"""
        try:
            page.goto(url, timeout=20000)
            page.wait_for_timeout(wait * 1000)
            title = page.title()
            body = ""
            try:
                body = page.inner_text("body")[:2000]
            except:
                pass
            return {"url": url, "title": title, "body_length": len(body), "ok": True}
        except Exception as e:
            return {"url": url, "error": str(e), "ok": False}

    def list_clickable(self, page) -> list[dict]:
        """列出页面上所有可点击的元素。"""
        elements = []
        for tag in ["a", "button", "[role='button']", "[onclick]"]:
            try:
                items = page.query_selector_all(tag)
                for el in items:
                    text = el.inner_text().strip()
                    href = el.get_attribute("href") or ""
                    if text and len(text) < 100:
                        elements.append({
                            "tag": tag,
                            "text": text[:80],
                            "href": href[:200],
                        })
            except:
                pass
        return elements

    def click_by_text(self, page, text: str, wait: int = 5) -> bool:
        """点击包含指定文本的元素。"""
        for tag in ["a", "button", "[role='button']"]:
            try:
                items = page.query_selector_all(tag)
                for el in items:
                    el_text = el.inner_text().strip()
                    if text in el_text:
                        print(f"  Clicking [{el_text}]")
                        el.click()
                        page.wait_for_timeout(wait * 1000)
                        return True
            except:
                pass
        return False

    def explore_urls(self, base_url: str, wait: int = 3) -> list[dict]:
        """尝试多种 URL 模式，找出可访问的校招页面。"""
        results = []
        print(f"Exploring career URLs for: {base_url}")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()
            page.on("response", self._on_response)

            for pattern in CAREER_URL_PATTERNS:
                url = pattern.format(base=base_url.rstrip("/"))
                result = self.visit_page(page, url, wait)
                status = "✅" if result["ok"] else "❌"
                print(f"  {status} {url}")

                if result["ok"]:
                    # 检查是否像校招页面
                    body = ""
                    try:
                        body = page.inner_text("body")
                    except:
                        pass
                    is_career = any(
                        kw in body
                        for kw in ["校招", "校园", "campus", "实习", "岗位", "职位", "招聘"]
                    )
                    result["is_career_page"] = is_career
                    result["body_preview"] = body[:300]
                    print(f"     Career page: {'Yes' if is_career else 'Probably not'}")

                results.append(result)

            browser.close()

        return results

    def browse_interactive(self, url: str, click_sequence: list[str] = None,
                           list_links: bool = False, pause: bool = False,
                           screenshot: str = None) -> dict:
        """交互式浏览指定页面。"""
        report = {
            "url": url,
            "visited": [],
            "apis": [],
            "links": [],
            "screenshot": None,
        }

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()
            page.on("response", self._on_response)

            # 访问主页面
            result = self.visit_page(page, url)
            report["visited"].append(result)

            if list_links:
                links = self.list_clickable(page)
                report["links"] = links
                print(f"\nFound {len(links)} clickable elements:")
                for i, link in enumerate(links[:30], 1):
                    print(f"  {i}. [{link['tag']}] {link['text']}")
                    if link["href"]:
                        print(f"     → {link['href']}")

            # 按顺序点击
            if click_sequence:
                for text in click_sequence:
                    text = text.strip()
                    if text:
                        print(f"\nLooking for: '{text}'")
                        success = self.click_by_text(page, text)
                        if success:
                            current_url = page.url
                            report["visited"].append({"url": current_url, "clicked": text})
                            print(f"  Current URL: {current_url}")
                        else:
                            print(f"  Element not found: '{text}'")

            # 截图
            if screenshot:
                page.screenshot(path=screenshot, full_page=True)
                report["screenshot"] = screenshot
                print(f"\nScreenshot → {screenshot}")

            # 暂停等待（调试模式）
            if pause and not self.headless:
                print("\n[DEBUG] Paused. Interact with the browser, then press Enter to continue...")
                input()

            browser.close()

        # 整理发现的 API
        seen_urls = set()
        for api in self.apis_found:
            # 去重 URL（去掉查询参数中的动态部分）
            base = api["url"].split("?")[0]
            if base not in seen_urls:
                seen_urls.add(base)
                report["apis"].append(api)

        return report


def generate_report(report: dict) -> str:
    """生成 API 发现报告的 Markdown。"""
    lines = [
        "# 校招 API 发现报告\n",
        f"> 时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"> 目标：{report['url']}",
        "",
    ]

    if report.get("apis"):
        lines.append("## 发现的 API\n")
        for i, api in enumerate(report["apis"], 1):
            api_type_desc = API_SIGNATURES.get(api["type"], {}).get("description", api["type"])
            lines.append(f"### API {i}: {api_type_desc}\n")
            lines.append(f"- **URL**: `{api['url'][:150]}`")
            lines.append(f"- **Status**: {api['status']}")
            if api.get("website_id"):
                lines.append(f"- **websiteId**: `{api['website_id']}`")
            if api.get("page_size"):
                lines.append(f"- **page_size**: {api['page_size']}")
            lines.append("")

        # 生成 fetch_jobs.py 示例命令
        lines.append("## 使用方法\n")
        lines.append("用 `fetch_jobs.py` 拉取岗位：\n")
        lines.append("```bash")
        for api in report["apis"]:
            if api.get("website_id"):
                # 构造 API URL（去掉查询参数）
                api_base = api["url"].split("?")[0]
                cmd = f"python scripts/fetch_jobs.py \\\n  --api-url \"{api_base}\" \\\n  --website-id {api['website_id']}"
                if api.get("page_size"):
                    cmd += f" \\\n  # 注意: page_size 上限为 {api['page_size']}"
                lines.append(cmd)
                break
        lines.append("```")
    else:
        lines.append("## 未发现已知 API\n")
        lines.append("可能需要：")
        lines.append("1. 使用 `--click-text` 交互后重试")
        lines.append("2. 使用 `--no-headless` 调试模式手动操作")
        lines.append("3. 检查是否有验证码/登录墙")

    if report.get("visited"):
        lines.append("\n## 访问的页面\n")
        for v in report["visited"]:
            lines.append(f"- {v.get('url', 'N/A')}")
            if v.get("clicked"):
                lines.append(f"  (点击: {v['clicked']})")

    if report.get("links"):
        lines.append(f"\n## 可点击元素 ({len(report['links'])})\n")
        for link in report["links"][:20]:
            lines.append(f"- [{link['tag']}] {link['text']}")
            if link["href"]:
                lines.append(f"  → {link['href']}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="通用校招页面浏览 & API 发现工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 探索模式：尝试多种 URL
  python scripts/browse_career.py --base-url "https://career.anker.com.cn" --explore

  # 指定页面 + 交互
  python scripts/browse_career.py \\
    --url "https://career.anker.com.cn/universities/recruitment" \\
    --click-sequence "投递岗位" --output api_report.json

  # 列出可点击元素
  python scripts/browse_career.py --url "https://career.anker.com.cn/campus" --list-links
        """,
    )

    parser.add_argument("--url", "-u", help="校招页面 URL")
    parser.add_argument("--base-url", "-b", help="企业招聘域名（配合 --explore）")
    parser.add_argument("--explore", action="store_true", help="探索模式")
    parser.add_argument("--click-sequence", "-c", help="点击顺序（逗号分隔）")
    parser.add_argument("--list-links", "-l", action="store_true", help="列出可点击元素")
    parser.add_argument("--no-headless", action="store_true", help="显示浏览器窗口")
    parser.add_argument("--pause", action="store_true", help="调试暂停")
    parser.add_argument("--wait", "-w", type=int, default=3, help="页面等待秒数")
    parser.add_argument("--output", "-o", help="输出报告 JSON 路径")
    parser.add_argument("--screenshot", "-s", help="截图路径")

    args = parser.parse_args()

    if not args.url and not args.base_url:
        parser.error("需要 --url 或 --base-url")

    browser = CareerBrowser(headless=not args.no_headless)

    # ── 探索模式 ──
    if args.explore:
        if not args.base_url:
            parser.error("探索模式需要 --base-url")
        results = browser.explore_urls(args.base_url, wait=args.wait)

        print(f"\n{'='*60}")
        accessible = [r for r in results if r.get("ok")]
        career_pages = [r for r in accessible if r.get("is_career_page")]
        print(f"Accessible: {len(accessible)}")
        print(f"Career pages: {len(career_pages)}")
        for cp in career_pages:
            print(f"  ✅ {cp['url']}")

        if args.output:
            report = {
                "base_url": args.base_url,
                "accessible": accessible,
                "career_pages": career_pages,
                "apis": browser.apis_found,
            }
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"\nSaved → {args.output}")
        return

    # ── 交互模式 ──
    click_seq = [s.strip() for s in args.click_sequence.split(",") if s.strip()] if args.click_sequence else None

    report = browser.browse_interactive(
        url=args.url,
        click_sequence=click_seq,
        list_links=args.list_links,
        pause=args.pause,
        screenshot=args.screenshot,
    )

    # 输出报告
    md_report = generate_report(report)
    print(f"\n{'='*60}")
    print(md_report)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\nSaved → {args.output}")

        # 同时保存 Markdown 报告
        md_path = Path(args.output).with_suffix(".md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_report)
        print(f"Saved Markdown → {md_path}")


if __name__ == "__main__":
    main()
