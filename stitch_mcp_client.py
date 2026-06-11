import urllib.request
import json
import ssl
import sys
import os

def load_dotenv():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip()

load_dotenv()

class StitchMCPClient:
    def __init__(self, api_key=None):
        if api_key is None:
            # Fallback to STITCH_API_KEY env variable or check .env
            api_key = os.environ.get("STITCH_API_KEY", "")
            
        self.url = "https://stitch.googleapis.com/mcp"
        self.headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key
        }
        self.ctx = ssl._create_unverified_context()

    def _call(self, method, params):
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        }
        req = urllib.request.Request(
            self.url,
            data=json.dumps(payload).encode('utf-8'),
            headers=self.headers,
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, context=self.ctx) as response:
                res = json.loads(response.read().decode('utf-8'))
                if "error" in res:
                    raise Exception(res["error"])
                return res.get("result", {})
        except Exception as e:
            print(f"Error calling {method}: {e}", file=sys.stderr)
            raise e

    def call_tool(self, tool_name, arguments):
        return self._call("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })

if __name__ == "__main__":
    # If run directly, allow calling from command line
    if len(sys.argv) < 2:
        print("Usage: python stitch_mcp_client.py <tool_name> [json_arguments]")
        sys.exit(1)
    
    tool = sys.argv[1]
    args = {}
    if len(sys.argv) >= 3:
        try:
            args = json.loads(sys.argv[2])
        except Exception as e:
            print(f"Error parsing JSON arguments: {e}", file=sys.stderr)
            sys.exit(1)
            
    client = StitchMCPClient()
    try:
        result = client.call_tool(tool, args)
        print(json.dumps(result, indent=2))
    except Exception as e:
        sys.exit(1)
