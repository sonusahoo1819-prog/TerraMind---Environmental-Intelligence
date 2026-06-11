import urllib.request
import json
import ssl
import sys
import os
import re

# Add path for stitch client
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from stitch_mcp_client import StitchMCPClient

# Configure SSL context to bypass verification on Windows if needed
ctx = ssl._create_unverified_context()

def parse_baton():
    baton_path = ".stitch/next-prompt.md"
    if not os.path.exists(baton_path):
        raise FileNotFoundError(f"Baton file {baton_path} not found.")
        
    with open(baton_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Extract YAML frontmatter
    yaml_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
    if not yaml_match:
        raise ValueError("Invalid next-prompt.md format. Missing frontmatter.")
        
    yaml_text = yaml_match.group(1)
    prompt_text = yaml_match.group(2).strip()
    
    page = "index"
    for line in yaml_text.split("\n"):
        if line.startswith("page:"):
            page = line.split(":", 1)[1].strip()
            
    return page, prompt_text

def download_file(url, filepath):
    print(f"Downloading {url} to {filepath}...")
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            with open(filepath, "wb") as f:
                f.write(response.read())
        print(f"Successfully saved to {filepath}")
    except Exception as e:
        print(f"Failed to download {filepath}: {e}", file=sys.stderr)
        raise e

def main():
    project_id = "5315967807671969055"
    design_system_id = "assets/13729526894684717540"
    
    try:
        page, prompt = parse_baton()
        print(f"Starting generation for page: {page}")
        
        client = StitchMCPClient()
        
        payload = {
            "projectId": project_id,
            "prompt": prompt,
            "designSystem": design_system_id,
            "deviceType": "DESKTOP"
        }
        
        print("Calling generate_screen_from_text tool on Stitch MCP (this can take a few minutes)...")
        result = client.call_tool("generate_screen_from_text", payload)
        
        # Try to parse the result
        sc = result.get("structuredContent", {})
        output_components = sc.get("outputComponents", [])
        
        if not output_components and "content" in result:
            # Fallback: parse JSON text from content
            text_content = result["content"][0].get("text", "")
            try:
                parsed_text = json.loads(text_content)
                output_components = parsed_text.get("outputComponents", [])
            except:
                pass
                
        if not output_components:
            print("Error: Could not find outputComponents in response.", file=sys.stderr)
            print(json.dumps(result, indent=2), file=sys.stderr)
            sys.exit(1)
            
        # Extract design screen info
        screen = None
        for component in output_components:
            if "design" in component:
                screens = component["design"].get("screens", [])
                if screens:
                    screen = screens[0]
                    break
                    
        if not screen:
            print("Error: Could not find screen design in output components.", file=sys.stderr)
            print(json.dumps(output_components, indent=2), file=sys.stderr)
            sys.exit(1)
            
        screen_id = screen.get("id")
        html_url = screen.get("htmlCode", {}).get("downloadUrl")
        screenshot_url = screen.get("screenshot", {}).get("downloadUrl")
        width = screen.get("width", 1440)
        
        print(f"Generated screen ID: {screen_id}")
        
        # Prepare destinations
        os.makedirs(".stitch/designs", exist_ok=True)
        html_dest = f".stitch/designs/{page}.html"
        png_dest = f".stitch/designs/{page}.png"
        
        if html_url:
            download_file(html_url, html_dest)
        else:
            print("Warning: HTML download URL is missing.")
            
        if screenshot_url:
            # Append width parameter to get high-res screenshot
            screenshot_full_url = f"{screenshot_url}=w{width}"
            download_file(screenshot_full_url, png_dest)
        else:
            print("Warning: Screenshot download URL is missing.")
            
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
            print("Updated .stitch/metadata.json with new screen reference.")
            
    except Exception as e:
        print(f"Execution failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
