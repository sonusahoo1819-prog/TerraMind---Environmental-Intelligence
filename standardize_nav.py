import os
import re

dest_dir = "site/public"
pages = [
    "index", "dashboard", "calculator", "aicoach", "challenges", 
    "community", "planner", "simulator", "marketplace"
]

def generate_header(active_page):
    links = [
        ("index.html", "Home", "index"),
        ("dashboard.html", "Dashboard", "dashboard"),
        ("calculator.html", "Calculator", "calculator"),
        ("aicoach.html", "AI Coach", "aicoach"),
        ("challenges.html", "Challenges", "challenges"),
        ("community.html", "Community", "community"),
        ("planner.html", "Planner", "planner"),
        ("simulator.html", "Simulator", "simulator"),
        ("marketplace.html", "Rewards", "marketplace")
    ]
    
    links_html = ""
    for href, label, name in links:
        if name == active_page:
            # Active tab styling
            links_html += f'<a class="text-primary border-b-2 border-primary pb-1 font-bold font-label-md text-label-md" href="{href}">{label}</a>\n'
        else:
            # Inactive tab styling
            links_html += f'<a class="text-on-surface-variant hover:text-on-surface transition-colors font-label-md text-label-md" href="{href}">{label}</a>\n'
            
    header_html = f"""<!-- Universal TopNavBar -->
<nav class="fixed top-4 left-1/2 -translate-x-1/2 w-[95%] rounded-xl bg-surface-glass backdrop-blur-2xl border border-outline-glass shadow-md shadow-glow-primary/10 flex justify-between items-center px-6 py-3 max-w-container-max mx-auto z-50">
    <div class="font-display-lg text-headline-md font-bold text-primary tracking-tight cursor-pointer" onclick="window.location.href='index.html'">TerraMind</div>
    <div class="hidden lg:flex items-center space-x-6">
        {links_html}
    </div>
    <button class="bg-primary text-on-primary px-4 py-1.5 rounded-full font-label-md text-label-md scale-95 active:scale-90 transition-transform shadow-lg shadow-glow-primary hover:brightness-110" onclick="window.location.href='aicoach.html'">
        Eco Coach
    </button>
</nav>"""
    return header_html

def main():
    for page in pages:
        filepath = os.path.join(dest_dir, f"{page}.html")
        if not os.path.exists(filepath):
            print(f"Skipping {page}: file not found.")
            continue
            
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        header_block = generate_header(page)
        
        # We need to replace the old navigation/header block.
        # Find <nav ...> ... </nav> or <header ...> ... </header> that sits near the top
        # Since Stitch creates nav or header tags, let's search for those and replace
        
        # Regex to match <nav> or <header> tags near top of page
        nav_pattern = r'<nav[^>]*>.*?</nav>'
        header_pattern = r'<header[^>]*>.*?</header>'
        
        # We replace the first occurrence of nav or header
        if re.search(nav_pattern, content, re.DOTALL):
            content = re.sub(nav_pattern, header_block, content, count=1, flags=re.DOTALL)
            print(f"Standardized <nav> header in {page}.html")
        elif re.search(header_pattern, content, re.DOTALL):
            content = re.sub(header_pattern, header_block, content, count=1, flags=re.DOTALL)
            print(f"Standardized <header> header in {page}.html")
        else:
            # Fallback: insert right after <body>
            body_start = re.search(r'<body[^>]*>', content)
            if body_start:
                content = content.replace(body_start.group(0), body_start.group(0) + "\n" + header_block)
                print(f"Injected header fallback after <body> in {page}.html")
                
        # Also standardize the footer links so they point to the correct files
        content = content.replace('href="#"', 'href="index.html"')
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

if __name__ == "__main__":
    main()
