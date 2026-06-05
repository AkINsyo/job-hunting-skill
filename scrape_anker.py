#!/usr/bin/env python3
"""Scrape Anker internship job listings."""
import sys
import json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # 拦截所有 XHR 请求，找 API
    api_responses = []
    def handle_response(response):
        url = response.url
        if "api" in url.lower() or "job" in url.lower() or "position" in url.lower() or "recruit" in url.lower():
            try:
                body = response.text()
                api_responses.append({"url": url, "status": response.status, "body": body[:2000]})
            except:
                api_responses.append({"url": url, "status": response.status, "body": "error reading"})
    
    page.on("response", handle_response)
    
    # 访问校招页面
    page.goto("https://career.anker.com.cn/universities/recruitment", timeout=30000)
    page.wait_for_timeout(3000)
    
    # 点击"投递岗位"按钮
    all_links = page.query_selector_all("a")
    for link in all_links:
        text = link.inner_text().strip()
        href = link.get_attribute("href") or ""
        if "投递岗位" in text:
            print(f"Clicking: [{text}] -> {href}")
            link.click()
            page.wait_for_timeout(8000)
            break
    
    print(f"\nCurrent URL: {page.url}")
    
    # 打印拦截到的 API 请求
    print(f"\n=== Intercepted {len(api_responses)} API responses ===")
    for resp in api_responses:
        print(f"\nURL: {resp['url']}")
        print(f"Status: {resp['status']}")
        if resp['body'] and len(resp['body']) > 10:
            print(f"Body: {resp['body'][:500]}")
    
    # 打印当前页面内容
    print(f"\n=== Page content ===")
    text = page.inner_text("body")
    print(text[:5000])
    
    browser.close()
