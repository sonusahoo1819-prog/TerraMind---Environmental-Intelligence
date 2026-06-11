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
TerraMind Carbon Reduction Planner.
A complete, high-fidelity responsive sustainability planner and roadmap page.

PLATFORM: Web, Desktop-first

PAGE STRUCTURE:
1. Header: Same floating navigation bar.
2. Main Content Layout:
   - Section 1: Hero-style header with title 'Carbon Reduction Planner' and subtitle 'Your customized step-by-step roadmap to net-zero carbon impact.'
   - Section 2: Interactive Roadmap Timeline representing the user's carbon journey:
     - Step 1 (Completed): 'Initial Audit' (8.5 tons base, checked state).
     - Step 3 (Active): 'Switching to Solar' (reduces 1.8 tons, in-progress state with progress indicator).
     - Step 4 (Planned): 'Commute Transition to EV' (reduces 2.2 tons, locked/future state).
     - Step 5 (Planned): 'Dietary Optimization' (reduces 1.2 tons, locked/future state).
     - Step 6 (Target): 'Net Zero Achievement' (Target: 1.5 tons/year).
   - Section 3: Recommended Action Items Card List (with priority tags and impact ratings):
     - Item 1: 'Upgrade all home lighting to LEDs' (High impact, low cost, active button: 'Mark as Done').
     - Item 2: 'Reduce flight hours by 10%' (Medium impact, zero cost, active button: 'Mark as Done').
     - Item 3: 'Add Composting to waste routing' (Medium impact, low cost, active button: 'Mark as Done').
   - Section 4: Potential Savings Card showing two large stat callouts side-by-side: 'Estimated CO2 Saved: 5.2 Tons/Yr' and 'Estimated Cost Savings: $1,420/Yr'.
3. Footer: Same minimal footer.
"""

payload = {
    "projectId": project_id,
    "prompt": prompt,
    "designSystem": design_system_id,
    "deviceType": "DESKTOP"
}

try:
    print("Generating planner page...")
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
            with open(".stitch/designs/planner.html", "wb") as f:
                f.write(html_content)
        print("Saved to .stitch/designs/planner.html")
    else:
        print("Error: HTML download URL is missing.")
        
except Exception as e:
    print(f"Error occurred: {e}")
