#!/usr/bin/env python3
"""Browse Anker campus recruitment - try different navigation approaches."""
import json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    api_data = []
    def handle_response(response):
        url = response.url
        if "rainbow-recall.anker.com.cn" in url:
            try:
                body = response.text()
                api_data.append({"url": url, "body": json.loads(body)})
            except:
                pass
    page.on("response", handle_response)
    
    # 直接访问校招岗位表页面
    urls_to_try = [
        "https://career.anker.com.cn/universities/recruitment/job-table",
        "https://career.anker.com.cn/universities/job-table",
        "https://career.anker.com.cn/universities/recruitment/job-list",
    ]
    
    for url in urls_to_try:
        print(f"\nTrying: {url}")
        try:
            page.goto(url, timeout=15000)
            page.wait_for_timeout(5000)
            text = page.inner_text("body")
            if "岗位" in text or "职位" in text or len(text) > 1000:
                print(f"Success! Content length: {len(text)}")
                print(text[:3000])
                break
            else:
                print(f"Content too short: {len(text)}")
        except Exception as e:
            print(f"Failed: {e}")
    
    # 尝试点击校招分类中的"投递岗位"
    print("\n\n=== 尝试点击'校园招聘'的'投递岗位' ===")
    page.goto("https://career.anker.com.cn/universities/recruitment", timeout=30000)
    page.wait_for_timeout(3000)
    
    # 找到所有包含"投递岗位"的链接
    links = page.query_selector_all("a")
    for link in links:
        text = link.inner_text().strip()
        if "投递岗位" in text:
            href = link.get_attribute("href") or ""
            # 获取父元素文本
            parent_text = link.evaluate("el => el.parentElement?.parentElement?.textContent || ''")
            print(f"  Link: [{text}] href={href}")
            print(f"  Context: {parent_text[:100]}")
            
            # 如果父元素包含"校园招聘"，点击它
            if "校园招聘" in parent_text and "实习" not in parent_text:
                print(f"  -> 点击校园招聘的投递岗位")
                link.click()
                page.wait_for_timeout(8000)
                print(f"  -> URL: {page.url}")
                new_text = page.inner_text("body")
                print(f"  -> Content: {new_text[:2000]}")
                
                # 截图
                page.screenshot(path="E:/AiWorkspace/job-hunting-skill/anker_job_table.png", full_page=True)
                break
    
    # 打印拦截到的 API
    print(f"\n=== 拦截到 {len(api_data)} 个 API ===")
    for api in api_data:
        print(f"  {api['url']}")
        body = api.get('body', {})
        if isinstance(body, dict) and 'data' in body:
            items = body['data'].get('items', [])
            if items:
                print(f"  -> {len(items)} items")
                for item in items[:3]:
                    print(f"     {item.get('title', '')} | {item.get('city', {}).get('zh_name', '')}")
    
    browser.close()
