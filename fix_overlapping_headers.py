import os
import re

dest_dir = "site/public"
pages_to_fix = ["community", "planner", "simulator", "marketplace"]

for page in pages_to_fix:
    filepath = os.path.join(dest_dir, f"{page}.html")
    if not os.path.exists(filepath):
        continue
        
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Remove the <header>...</header> block completely
    # We match <header ...> followed by anything until </header>
    header_pattern = r'<header[^>]*>.*?</header>'
    
    if re.search(header_pattern, content, re.DOTALL):
        # We replace the header block with an empty string
        content = re.sub(header_pattern, "", content, count=1, flags=re.DOTALL)
        print(f"Removed overlapping <header> tag in {page}.html")
        
        # Save the updated file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
    else:
        print(f"No <header> tag found in {page}.html")
