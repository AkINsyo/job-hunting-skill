#!/usr/bin/env python3
"""Fetch Anker internship positions in Changsha via API."""
import json
import urllib.request

base_url = "https://rainbow-recall.anker.com.cn/api/lark/hire/v1/jobs"
website_id = "6962795203808217351"

# 尝试多种参数组合
params_list = [
    f"page_size=20&websiteId={website_id}&city_code=CT_20",
    f"page_size=20&websiteId={website_id}&city=CT_20",
    f"page_size=20&websiteId={website_id}",
]

for params in params_list:
    url = f"{base_url}?{params}"
    print(f"\n=== Trying: {url} ===")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            if data.get("code") == 0 and "data" in data:
                items = data["data"].get("items", [])
                print(f"Total items: {len(items)}")
                
                # 过滤长沙的岗位
                changsha_jobs = []
                for job in items:
                    city = job.get("city", {})
                    city_name = city.get("zh_name", "")
                    city_list = job.get("city_list", [])
                    city_names = [c.get("name", {}).get("zh_cn", "") for c in city_list]
                    
                    if "长沙" in city_name or "长沙" in city_names:
                        title = job.get("title", "")
                        desc = job.get("description", "")[:200]
                        req_text = job.get("requirement", "")[:200]
                        func = job.get("job_function", {}).get("name", {}).get("zh_cn", "")
                        rec_type = job.get("recruitment_type", {}).get("zh_name", "")
                        dept = job.get("department", {}).get("zh_name", "")
                        subject = job.get("subject", {}).get("name", {}).get("zh_cn", "")
                        
                        changsha_jobs.append({
                            "title": title,
                            "city": city_name,
                            "function": func,
                            "type": rec_type,
                            "dept": dept,
                            "subject": subject,
                            "desc": desc,
                            "requirement": req_text,
                            "code": job.get("code", ""),
                            "id": job.get("id", ""),
                        })
                
                print(f"Changsha jobs: {len(changsha_jobs)}")
                for j in changsha_jobs:
                    print(f"\n  📌 {j['title']}")
                    print(f"     城市: {j['city']} | 类型: {j['type']} | 分类: {j['function']}")
                    print(f"     部门: {j['dept']} | 方向: {j['subject']}")
                    print(f"     编号: {j['code']}")
                    if j['desc']:
                        print(f"     描述: {j['desc'][:150]}...")
                    if j['requirement']:
                        print(f"     要求: {j['requirement'][:150]}...")
                
                if changsha_jobs:
                    # 保存完整数据
                    with open("E:/AiWorkspace/job-hunting-skill/jobs/anker_changsha.json", "w", encoding="utf-8") as f:
                        json.dump(changsha_jobs, f, ensure_ascii=False, indent=2)
                    print(f"\nSaved to jobs/anker_changsha.json")
                    break
            else:
                print(f"Error: {data.get('msg', 'unknown')}")
    except Exception as e:
        print(f"Request failed: {e}")
