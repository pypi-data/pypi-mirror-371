#!/usr/bin/env python3
"""Test MCP server through actual protocol"""
import json
import subprocess
import sys

def send_request(request):
    """Send a request to MCP server and get response"""
    proc = subprocess.Popen(
        ['starbase-mcp-server'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Send request
    proc.stdin.write(json.dumps(request) + '\n')
    proc.stdin.flush()
    
    # Read response
    response_line = proc.stdout.readline()
    
    # Terminate
    proc.terminate()
    
    return json.loads(response_line) if response_line else None

# Test get_package_code
request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "get_package_code",
        "arguments": {
            "package_name": "thrivecart-design-system"
        }
    }
}

print("Sending MCP request for get_package_code...")
response = send_request(request)
print(f"Response: {json.dumps(response, indent=2)}")
