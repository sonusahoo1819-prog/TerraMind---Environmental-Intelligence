import os
import re

dest_dir = "site/public"
pages = [
    "index", "dashboard", "calculator", "aicoach", "challenges", 
    "community", "planner", "simulator", "marketplace"
]

for page in pages:
    filepath = os.path.join(dest_dir, f"{page}.html")
    if not os.path.exists(filepath):
        continue
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    headers = re.findall(r'<header[^>]*>', content)
    navs = re.findall(r'<nav[^>]*>', content)
    print(f"Page: {page}.html")
    print(f"  Headers found: {len(headers)}")
    for h in headers:
        print(f"    {h[:100]}")
    print(f"  Navs found: {len(navs)}")
    for n in navs:
        print(f"    {n[:100]}")
