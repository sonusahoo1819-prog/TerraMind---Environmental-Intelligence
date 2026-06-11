import os
import re

source_dir = ".stitch/designs"
dest_dir = "site/public"

pages = [
    "index", "dashboard", "calculator", "aicoach", "challenges", 
    "community", "planner", "simulator", "marketplace"
]

def wire_navigation(html):
    # Fix the navigation links across all pages
    # Home -> index.html
    # Dashboard -> dashboard.html
    # Calculator -> calculator.html
    # AI Coach -> aicoach.html
    # Challenges -> challenges.html
    # Community -> community.html
    # Rewards -> marketplace.html
    
    # We will search for <a> tags containing specific names and replace their hrefs
    replacements = [
        (r'href=["\'][^"\']*["\']([^>]*>Home</)', 'href="index.html"\\1'),
        (r'href=["\'][^"\']*["\']([^>]*>Dashboard</)', 'href="dashboard.html"\\1'),
        (r'href=["\'][^"\']*["\']([^>]*>Calculator</)', 'href="calculator.html"\\1'),
        (r'href=["\'][^"\']*["\']([^>]*>AI Coach</)', 'href="aicoach.html"\\1'),
        (r'href=["\'][^"\']*["\']([^>]*>Challenges</)', 'href="challenges.html"\\1'),
        (r'href=["\'][^"\']*["\']([^>]*>Community</)', 'href="community.html"\\1'),
        (r'href=["\'][^"\']*["\']([^>]*>Rewards</)', 'href="marketplace.html"\\1')
    ]
    
    for pattern, repl in replacements:
        html = re.sub(pattern, repl, html, flags=re.IGNORECASE)
        
    # Also fix secondary links like "Calculate My Footprint" buttons
    html = re.sub(r'Calculate My Footprint</button>', 'Calculate My Footprint</button>', html)
    
    # Wire click actions or links to main buttons
    # In index.html, wire the button to navigate to calculator.html
    html = html.replace('onclick="window.location.href=\'calculator.html\'"', '') # Clean old ones if any
    html = re.sub(
        r'(Calculate My Footprint</button>)',
        r'onclick="window.location.href=\'calculator.html\'" \1',
        html
    )
    html = re.sub(
        r'(Explore Journey</button>|Explore Sustainability Journey</button>)',
        r'onclick="window.location.href=\'planner.html\'" \1',
        html
    )
    
    return html

def inject_styles_and_scripts(page, html):
    # Inject style.css link in head
    style_link = '    <link rel="stylesheet" href="css/style.css">\n'
    html = html.replace('</head>', f'{style_link}</head>')
    
    # Inject page-specific scripts and CDN libraries
    script_injection = ""
    
    if page == "index":
        # Inject Three.js CDN and earth.js script
        three_js = '    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>\n'
        earth_script = '    <script src="js/earth.js"></script>\n'
        script_injection = f'{three_js}{earth_script}'
        
        # Insert a canvas element for ThreeJS inside the placeholder div
        # Find where "3D Earth Placeholder" is, or inside the glass panel div
        placeholder_regex = r'(<!-- Glassmorphic Container for 3D Visual -->\s*<div[^>]*>)'
        html = re.sub(
            placeholder_regex,
            r'\1\n            <canvas id="earth-canvas" class="w-full h-full absolute inset-0"></canvas>',
            html
        )
        
    elif page == "dashboard":
        # Inject Chart.js CDN and dashboard.js script
        chart_js = '    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>\n'
        dashboard_script = '    <script src="js/dashboard.js"></script>\n'
        script_injection = f'{chart_js}{dashboard_script}'
        
        # Replace chart divs with actual canvas elements
        # Donut Chart Container
        html = re.sub(
            r'<!-- Circular Progress \(SVG\) -->\s*<svg[^>]*>.*?</svg>',
            '<canvas id="emissions-donut-chart" class="w-full max-h-64"></canvas>',
            html,
            flags=re.DOTALL
        )
        # Weekly trends bar chart placeholder
        html = re.sub(
            r'<!-- Chart Bars -->.*?</div>\s*</div>',
            '<canvas id="trends-line-chart" class="w-full max-h-64"></canvas>\n</div>',
            html,
            flags=re.DOTALL
        )
        
    elif page == "calculator":
        calc_script = '    <script src="js/calculator.js"></script>\n'
        script_injection = f'{calc_script}'
        
    elif page == "aicoach":
        coach_script = '    <script src="js/aicoach.js"></script>\n'
        script_injection = f'{coach_script}'
        
    elif page == "simulator":
        sim_script = '    <script src="js/simulator.js"></script>\n'
        script_injection = f'{sim_script}'
        
    if script_injection:
        html = html.replace('</body>', f'{script_injection}</body>')
        
    return html

def main():
    os.makedirs(dest_dir, exist_ok=True)
    
    for page in pages:
        src_path = os.path.join(source_dir, f"{page}.html")
        dest_path = os.path.join(dest_dir, f"{page}.html")
        
        if not os.path.exists(src_path):
            print(f"Skipping {page}: source not found at {src_path}")
            continue
            
        with open(src_path, "r", encoding="utf-8") as f:
            html = f.read()
            
        # Wire links and navigation
        html = wire_navigation(html)
        
        # Inject styling links and scripts
        html = inject_styles_and_scripts(page, html)
        
        # Ensure all HTML links in the header are correctly mapped
        # Nav buttons pointing to other pages
        html = html.replace('href="#"', 'href="index.html"')
        
        with open(dest_path, "w", encoding="utf-8") as f:
            f.write(html)
            
        print(f"Integrated {src_path} -> {dest_path}")

if __name__ == "__main__":
    main()
