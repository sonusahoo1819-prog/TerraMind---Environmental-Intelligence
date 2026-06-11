from stitch_mcp_client import StitchMCPClient
import json
import os
import urllib.request
import ssl

client = StitchMCPClient()
project_id = "5315967807671969055"
design_system_id = "assets/13729526894684717540"
ctx = ssl._create_unverified_context()

prompt = """
TerraMind Landing Page.
A complete, high-fidelity responsive landing page.

PLATFORM: Web, Desktop-first

PAGE STRUCTURE:
1. Header: Sticky navigation bar with 'TerraMind' logo in emerald green, links for 'Home', 'Dashboard', 'Calculator', 'AI Coach', 'Challenges', 'Community', 'Rewards', and a 'Sign In' glassmorphic button.
2. Hero Section:
   - Left side: Bold headline 'Understand Your Impact. Shape a Sustainable Future.', subtext about tracking emissions and earning rewards, and two action buttons: 'Calculate My Footprint' and 'Explore Journey'.
   - Right side: Card placeholder with glassmorphic styling, showing global carbon clocks and dynamic energy statistics.
3. Stats Dashboard Preview: Three columns showing carbon score, weekly trends, and environmental XP status with sleek progress bars.
4. Features Showcase: A grid of 4 cards detailing: Smart Footprint Calculator, AI Sustainability Coach, Gamification Streaks, and Rewards Marketplace.
5. CTA Banner: Glassmorphic panel with headline 'Start Your Sustainability Journey Today' and a 'Get Started' button.
6. Footer: Minimal footer with company links and newsletter subscription.
"""

payload = {
    "projectId": project_id,
    "prompt": prompt,
    "designSystem": design_system_id,
    "deviceType": "DESKTOP"
}

try:
    print("Generating index page...")
    result = client.call_tool("generate_screen_from_text", payload)
    
    # Try to parse the result
    sc = result.get("structuredContent", {})
    output_components = sc.get("outputComponents", [])
    
    if not output_components and "content" in result:
        text_content = result["content"][0].get("text", "")
        try:
            parsed_text = json.loads(text_content)
            output_components = parsed_text.get("outputComponents", [])
        except:
            pass
            
    if not output_components:
        print("Error: Could not find outputComponents in response.")
        print(json.dumps(result, indent=2))
        exit(1)
        
    screen = None
    for component in output_components:
        if "design" in component:
            screens = component["design"].get("screens", [])
            if screens:
                screen = screens[0]
                break
                
    if not screen:
        print("Error: Could not find screen design in output components.")
        print(json.dumps(output_components, indent=2))
        exit(1)
        
    screen_id = screen.get("id")
    html_url = screen.get("htmlCode", {}).get("downloadUrl")
    print(f"Generated Page Screen ID: {screen_id}")
    
    if html_url:
        print(f"Downloading HTML from {html_url}...")
        req = urllib.request.Request(html_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=ctx) as response:
            html_content = response.read()
            with open(".stitch/designs/index.html", "wb") as f:
                f.write(html_content)
        print("Saved to .stitch/designs/index.html")
    else:
        print("Error: HTML download URL is missing.")
        
except Exception as e:
    print(f"Error occurred: {e}")
