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
        
    main_tags = re.findall(r'<main[^>]*>', content)
    first_sec = re.findall(r'<body[^>]*>\s*(?:<!--.*?-->\s*)*<nav[^>]*>.*?</nav>\s*<(section|div)[^>]*>', content, re.DOTALL)
    
    print(f"Page: {page}.html")
    for m in main_tags:
        print(f"  Main tag: {m}")
    if not main_tags:
        # Print the first tag after body/nav
        print("  No main tag found.")
