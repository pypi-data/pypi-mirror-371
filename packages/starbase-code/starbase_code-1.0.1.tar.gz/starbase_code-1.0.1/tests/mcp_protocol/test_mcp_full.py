#!/usr/bin/env python3
import json
import subprocess
import sys

def mcp_call(method, params=None):
    """Make an MCP call"""
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or {}
    }
    
    proc = subprocess.Popen(
        ['starbase-mcp-server'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Initialize first
    init_req = {
        "jsonrpc": "2.0",
        "id": 0,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1.0.0"}
        }
    }
    proc.stdin.write(json.dumps(init_req) + '\n')
    proc.stdin.flush()
    _ = proc.stdout.readline()  # Read init response
    
    # Send actual request
    proc.stdin.write(json.dumps(request) + '\n')
    proc.stdin.flush()
    
    response = proc.stdout.readline()
    proc.terminate()
    
    return json.loads(response) if response else None

# Call get_package_code
print("Calling get_package_code through MCP protocol...")
result = mcp_call("tools/call", {
    "name": "get_package_code",
    "arguments": {"package_name": "thrivecart-design-system"}
})

if result and "result" in result:
    res = result["result"]
    print(f"Success! Package: {res.get('package', 'N/A')}")
    print(f"File count: {res.get('file_count', 0)}")
    files = res.get('files', {})
    print(f"Files dict type: {type(files)}")
    print(f"Files dict empty? {len(files) == 0}")
    if files:
        print(f"Files found: {list(files.keys())[:5]}")
    else:
        print("Files dict is EMPTY!")
        print(f"Full result keys: {list(res.keys())}")
        print(f"Full result: {json.dumps(res, indent=2)[:500]}")
else:
    print(f"Error: {json.dumps(result, indent=2)}")
