from stitch_mcp_client import StitchMCPClient
import json
import os
import urllib.request
import ssl
import time

client = StitchMCPClient()
project_id = "5315967807671969055"
design_system_id = "assets/13729526894684717540"
ctx = ssl._create_unverified_context()

prompts = {
    "dashboard": """
TerraMind Sustainability Dashboard.
A complete, high-fidelity responsive dashboard page.

PLATFORM: Web, Desktop-first

PAGE STRUCTURE:
1. Header: Same floating navigation bar.
2. Grid Layout:
   - Card 1 (Personal Carbon Score): Large dial or gauge showing 'Your Carbon Score: 78 / 100'. Status message 'On Track for Monthly Target'.
   - Card 2 (Monthly Emissions): Space for a donut chart breaking down: Transportation, Electricity, Food, Travel, Waste.
   - Card 3 (Weekly Progress): Space for a smooth line chart showing carbon reduction over the last 4 weeks.
   - Card 4 (Reduction Trends): Dynamic list of recent savings (e.g. 'Switched to public transport: -12kg Co2', 'Meat-free meals: -4kg Co2').
   - Card 5 (Impact Heatmap): Large matrix or map displaying regional impact and community efforts.
3. Footer: Same minimal footer.
""",
    "calculator": """
TerraMind Smart Footprint Calculator.
An interactive, high-fidelity multi-category footprint calculator.

PLATFORM: Web, Desktop-first

PAGE STRUCTURE:
1. Header: Same navigation bar.
2. Active Carbon Score Indicator: Floating header showing dynamic footprint score updating live.
3. Interactive 3D Cards Grid:
   - Card 1: Transportation (inputs for car mileage, public transit hours, EV charging).
   - Card 2: Electricity Usage (inputs for monthly bill, solar percentage).
   - Card 3: Food Habits (selections for meat, plant-based, dairy usage).
   - Card 4: Travel & Flight (inputs for flight hours, hotel stays).
   - Card 5: Waste Management (inputs for recycling rate, composting).
4. Real-time Carbon Score Card: A large dashboard panel showing carbon score gauge, estimated annual Co2 tonnage, and comparison to national averages.
5. Action CTAs: 'Save Footprint Data', 'View Coach Recommendations'.
6. Footer.
""",
    "aicoach": """
TerraMind AI Sustainability Coach.
A premium, highly interactive conversational coaching panel.

PLATFORM: Web, Desktop-first

PAGE STRUCTURE:
1. Header: Same navigation bar.
2. Left Column (Daily Intelligence):
   - Daily Eco-Tip Card: 'Save water during showers today. Potential Co2 savings: 0.8kg.'
   - Goal-Setting panel: List of active goals (e.g. 'Install LED bulbs', 'Carpool 3 times a week').
3. Right Column (AI Chatbot Interface):
   - A modern chat window themed with dark green glow accents.
   - Dialogue messages from 'Coach Terra' recommending actions based on carbon metrics.
   - Message input field with glassmorphism style and a quick suggestion buttons panel (e.g. 'Suggest an easy eco-tip', 'How do I offset my flight?', 'Review my planner').
4. Footer.
""",
    "challenges": """
TerraMind Gamification & Challenges.
A premium gaming-inspired achievement and streaks page.

PLATFORM: Web, Desktop-first

PAGE STRUCTURE:
1. Header: Same navigation.
2. User Progress Bar: XP points (Level 24, 24,500/30,000 XP), active streak (12 Days Eco Streak).
3. Weekly Challenges: A list of active group quests (e.g. 'Public Transit Week', 'Zero Waste Weekend') with reward badges and XP counts.
4. Badges Grid: Icons for achievements like 'Forest Protector', 'Solar Powered', 'EV Pioneer' in unlocked (glowing eco-lime) and locked (semi-transparent glass) states.
5. Community Leaderboard: A beautiful list ranking top users with avatar frames, streaks, and total XP.
6. Footer.
""",
    "community": """
TerraMind Community Hub.
An interactive cards layout for social groups, discussions, and events.

PLATFORM: Web, Desktop-first

PAGE STRUCTURE:
1. Header: Same navigation.
2. Filter Tabs: 'Active Groups', 'Local Events', 'Discussions', 'Team Challenges'.
3. Groups Grid: Glassmorphic cards for 'Solar Energy Collective', 'Urban Composting Association', 'Zero Emission Commuters', showing member counts and join buttons.
4. Local Events Section: Timeline or cards showing upcoming community tree-planting days and EV meetups.
5. Discussion Forum: Brief previews of popular posts and threads with upvotes and reply metrics.
6. Footer.
""",
    "planner": """
TerraMind Carbon Reduction Planner.
An animated sustainability roadmap and action journey planner.

PLATFORM: Web, Desktop-first

PAGE STRUCTURE:
1. Header: Same navigation.
2. Visual Roadmap: An animated timeline representing the user's journey from 'Current Footprint: 8.5 tons' -> 'Switching to Solar (-1.8t)' -> 'EV Transition (-3.2t)' -> 'Net Zero Milestone'.
3. Recommended Actions: Priority list of tasks sorted by cost and impact.
4. Potential Savings Card: Interactive panel showing total carbon and financial savings if roadmap is followed.
5. Footer.
""",
    "simulator": """
TerraMind Carbon Impact Simulator.
An interactive 'What happens if I...' slider-based impact playground.

PLATFORM: Web, Desktop-first

PAGE STRUCTURE:
1. Header: Same navigation.
2. Slider Playground Panel:
   - Slider 1: Public Transport Usage (0% to 100%)
   - Slider 2: Renewable Energy Powering Home (0% to 100%)
   - Slider 3: Meat Consumption (Every day to Vegan)
   - Slider 4: Commuting (EV vs Gas car)
3. Live Environmental Impact Visualizer: A large screen split displaying the instant effect.
   - Text reading 'Your changes would save 4.2 tons of Co2 annually.'
   - Visual comparison showing equivalence: 'Equivalent to planting 192 trees' and 'Saving $850 in fuel/power bills'.
4. Footer.
""",
    "marketplace": """
TerraMind Rewards Marketplace.
A premium product catalog for redeeming eco points.

PLATFORM: Web, Desktop-first

PAGE STRUCTURE:
1. Header: Same navigation.
2. User Credits Panel: Showing 'Available TerraCredits: 4,500' and 'Total Tree Credits: 8'.
3. Voucher Card Grid:
   - Item 1: 'Plant a Tree in the Amazon' (500 credits)
   - Item 2: 'Sustainable Bamboo Kitchen Set' (1,200 credits)
   - Item 3: '$10 Donation to Clean Ocean NGO' (800 credits)
   - Item 4: 'Official Carbon Offset Certificate' (1,500 credits)
4. Redemptions History: Recent vouchers redeemed.
5. Footer.
"""
}

def download_html(url, dest):
    print(f"Downloading {url} to {dest}...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=ctx) as response:
        with open(dest, "wb") as f:
            f.write(response.read())
    print(f"Saved to {dest}")

def generate_page(page, prompt):
    print(f"\n======================================")
    print(f"Generating page: {page}")
    print(f"======================================")
    
    payload = {
        "projectId": project_id,
        "prompt": prompt,
        "designSystem": design_system_id,
        "deviceType": "DESKTOP"
    }
    
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
        raise ValueError(f"Could not find outputComponents in response for page: {page}")
        
    screen = None
    for component in output_components:
        if "design" in component:
            screens = component["design"].get("screens", [])
            if screens:
                screen = screens[0]
                break
                
    if not screen:
        raise ValueError(f"Could not find screen design in output components for page: {page}")
        
    screen_id = screen.get("id")
    html_url = screen.get("htmlCode", {}).get("downloadUrl")
    print(f"Page {page} Screen ID: {screen_id}")
    
    if html_url:
        dest_path = f".stitch/designs/{page}.html"
        download_html(html_url, dest_path)
        
        # Update metadata.json screens map
        meta_path = ".stitch/metadata.json"
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            
            meta.setdefault("screens", {})
            meta["screens"][page] = {
                "id": screen_id,
                "sourceScreen": f"projects/{project_id}/screens/{screen_id}",
                "width": screen.get("width"),
                "height": screen.get("height")
            }
            
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2)
            print(f"Updated .stitch/metadata.json with screen {page}")
    else:
        raise ValueError(f"HTML download URL missing for page: {page}")

def main():
    os.makedirs(".stitch/designs", exist_ok=True)
    success = []
    failed = []
    
    for page, prompt in prompts.items():
        # Check if already exists to allow resumption
        dest_path = f".stitch/designs/{page}.html"
        if os.path.exists(dest_path) and os.path.getsize(dest_path) > 100:
            print(f"Page {page} already exists, skipping generation.")
            success.append(page)
            continue
            
        try:
            generate_page(page, prompt)
            success.append(page)
            # Sleep a short duration to avoid rate limits
            time.sleep(2)
        except Exception as e:
            print(f"Failed to generate {page}: {e}")
            failed.append(page)
            
    print("\nGeneration Summary:")
    print(f"Successful ({len(success)}): {', '.join(success)}")
    print(f"Failed ({len(failed)}): {', '.join(failed)}")
    
    if failed:
        sys.exit(1)

if __name__ == "__main__":
    main()
