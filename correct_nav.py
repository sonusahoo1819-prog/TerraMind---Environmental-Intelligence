import os
import re

dest_dir = "site/public"
source_dir = ".stitch/designs"

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

def clean_and_inject(page, html):
    # 1. Identify and remove any top-level header/nav blocks created by Stitch
    # In index, dashboard, calculator, aicoach, challenges, etc., they might have <nav> or <header>
    # We want to remove the SITE header (usually the first <header> or <nav> in the body)
    # But wait, dashboard/calculator/aicoach have content headers. We must NOT remove content headers!
    # Content headers don't have classes like "sticky", "fixed", "w-full", "top-0", "top-4", etc.
    # Site headers usually have layout classes:
    # - fixed w-full top-0
    # - sticky top-0
    # - fixed top-4
    # Let's target these patterns specifically!
    
    site_header_patterns = [
        # Match navigation bars with fixed/sticky positioning at top
        r'<nav[^>]*class="[^"]*(fixed|sticky|top-)[^"]*"[^>]*>.*?</nav>',
        r'<header[^>]*class="[^"]*(fixed|sticky|top-)[^"]*"[^>]*>.*?</header>'
    ]
    
    for pattern in site_header_patterns:
        html = re.sub(pattern, "", html, count=1, flags=re.DOTALL | re.IGNORECASE)
        
    # Also clean up any standard <a> navigation links that might be floating around
    # 2. Inject our unified header block directly after <body> start tag
    header_block = generate_header(page)
    body_start_pattern = r'(<body[^>]*>)'
    
    html = re.sub(body_start_pattern, r'\1\n' + header_block, html, count=1, flags=re.IGNORECASE)
    
    # 3. Prevent content from overlapping under the fixed navbar
    if page == "dashboard":
        # Replace the SVG donut chart with a Canvas element and reduce gap size
        html = re.sub(
            r'<div class="flex items-center gap-md">\s*<div class="relative w-32 h-32 flex-shrink-0">\s*<svg[^>]*>.*?</svg>\s*</div>',
            '<div class="flex items-center gap-sm">\n<div class="relative w-28 h-28 flex-shrink-0">\n<canvas id="emissions-donut-chart" class="w-full h-full"></canvas>\n</div>',
            html,
            flags=re.DOTALL
        )
        # Replace the SVG line chart with a Canvas element
        html = re.sub(
            r'<svg class="w-full h-full overflow-visible" preserveaspectratio="none">.*?</svg>',
            '<canvas id="trends-line-chart" class="w-full h-full"></canvas>',
            html,
            flags=re.DOTALL
        )
    elif page == "index":
        # index.html uses pt-xl (64px) on mobile, change to pt-32 (128px) so mobile has enough space. md:pt-48 handles desktop.
        html = html.replace('pt-xl pb-24 md:pt-48 md:pb-32 px-sm md:px-xl', 'pt-32 pb-24 md:pt-48 md:pb-32 px-sm md:px-xl')
        
        # Futuristic Glassmorphic Preloader HTML overlay
        preloader_html = """
<!-- Futuristic Glassmorphic Preloader -->
<div id="preloader" class="fixed inset-0 bg-[#0e150f] z-[9999] flex flex-col items-center justify-center transition-all duration-700 ease-out">
    <div class="absolute w-72 h-72 rounded-full bg-primary/10 blur-[80px] animate-pulse"></div>
    <div class="relative flex flex-col items-center gap-6 text-center">
        <div class="relative w-20 h-20">
            <div class="absolute inset-0 rounded-full border-4 border-primary/20"></div>
            <div class="absolute inset-0 rounded-full border-4 border-primary border-t-transparent animate-spin"></div>
            <div class="absolute inset-0 flex items-center justify-center">
                <span class="material-symbols-outlined text-primary text-3xl animate-pulse">eco</span>
            </div>
        </div>
        <div>
            <h2 class="font-display-lg text-headline-lg font-bold text-primary tracking-tight mb-2">TerraMind</h2>
            <p class="text-on-surface-variant font-label-md text-label-md tracking-widest uppercase animate-pulse">Environmental Intelligence Loading...</p>
        </div>
    </div>
</div>
"""
        # Script to fade out preloader on window load
        preloader_js = """
    <script>
        window.addEventListener('load', () => {
            const preloader = document.getElementById('preloader');
            if (preloader) {
                setTimeout(() => {
                    preloader.classList.add('opacity-0', 'pointer-events-none');
                    setTimeout(() => { preloader.remove(); }, 700);
                }, 1500); // 1.5s visual showcase
            }
        });
    </script>
</body>"""
        
        # Insert preloader HTML at body start
        html = re.sub(body_start_pattern, r'\1\n' + preloader_html, html, count=1, flags=re.IGNORECASE)
        # Insert fade-out script
        html = html.replace('</body>', preloader_js)
    elif page == "planner":
        # planner.html uses py-12 on main, change to pt-32 pb-12
        html = html.replace('<main class="max-w-7xl mx-auto px-6 py-12 space-y-20">', '<main class="max-w-7xl mx-auto px-6 pt-32 pb-12 space-y-20">')
    elif page == "simulator":
        # simulator.html uses py-12 on the inner container, and main has no padding. We put pt-32 on main and pb-12 on the inner container.
        html = html.replace('<main class="relative min-h-screen">', '<main class="relative min-h-screen pt-32">')
        html = html.replace('<div class="relative z-10 max-w-7xl mx-auto px-6 py-12">', '<div class="relative z-10 max-w-7xl mx-auto px-6 pb-12">')
    elif page == "marketplace":
        # marketplace.html uses pt-24 pb-16 on main, change to pt-32 pb-16
        html = html.replace('<main class="pt-24 pb-16 px-6 md:px-12 max-w-7xl mx-auto w-full flex-grow">', '<main class="pt-32 pb-16 px-6 md:px-12 max-w-7xl mx-auto w-full flex-grow">')
        
    return html

def main():
    # Run integration script first to refresh public files from clean designs
    print("Restoring public files from designs...")
    os.system("python C:\\Users\\Asus\\.gemini\\antigravity\\scratch\\terramind\\integrate_pages.py")
    
    for page in pages:
        filepath = os.path.join(dest_dir, f"{page}.html")
        if not os.path.exists(filepath):
            continue
            
        with open(filepath, "r", encoding="utf-8") as f:
            html = f.read()
            
        # Clean overlapping navigation headers and inject our standardized one
        html = clean_and_inject(page, html)
        
        # Save standard output
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
            
        print(f"Standardized and injected navigation in {page}.html")

if __name__ == "__main__":
    main()
