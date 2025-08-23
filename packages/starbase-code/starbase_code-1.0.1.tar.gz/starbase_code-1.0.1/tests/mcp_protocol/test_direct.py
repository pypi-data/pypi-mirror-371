import sys
import json
from pathlib import Path

# Mock FastMCP just for testing
class MockMCP:
    def tool(self):
        def decorator(func):
            return func
        return decorator

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
    print(f'  File keys: {list(files.keys())}')
    # Check content of first file
    first_key = list(files.keys())[0]
    content = files[first_key]
    print(f'  First file ({first_key}) content type: {type(content)}')
    if isinstance(content, dict):
        print(f'    Content keys: {list(content.keys())}')
    else:
        print(f'    Content length: {len(str(content))}')
