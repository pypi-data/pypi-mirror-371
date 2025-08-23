import sys
import json
from pathlib import Path

# Mock FastMCP properly
class MockMCP:
    def __init__(self, name):
        self.name = name
    def tool(self):
        def decorator(func):
            return func
        return decorator
    def run(self, transport='stdio'):
        pass

sys.modules['mcp'] = type(sys)('mcp')
sys.modules['mcp.server'] = type(sys)('mcp.server')
sys.modules['mcp.server.fastmcp'] = type(sys)('mcp.server.fastmcp')
sys.modules['mcp.server.fastmcp'].FastMCP = MockMCP

# Now import our module
sys.path.insert(0, '/Users/t/dev/area51/starbase/src')
from starbase import mcp_server

# Test the function directly
result = mcp_server.get_package_code('thrivecart-design-system')
print(f'Direct call result:')
print(f'  Package: {result.get("package")}')
print(f'  File count: {result.get("file_count")}')
print(f'  Files in result: {"files" in result}')
files = result.get("files", {})
print(f'  Files type: {type(files)}')
print(f'  Files length: {len(files)}')
if files:
    file_keys = list(files.keys())
    print(f'  File keys: {file_keys}')
    # Check content of each file
    for key in file_keys:
        content = files[key]
        if isinstance(content, dict):
            print(f'  {key}: dict with keys {list(content.keys())}')
        else:
            print(f'  {key}: {type(content).__name__} of length {len(str(content))}')
else:
    print('  ERROR: Files dict is EMPTY!')

# Also test JSON serialization
try:
    json_str = json.dumps(result)
    print(f'\nJSON serialization: SUCCESS ({len(json_str)} bytes)')
except Exception as e:
    print(f'\nJSON serialization: FAILED - {e}')
