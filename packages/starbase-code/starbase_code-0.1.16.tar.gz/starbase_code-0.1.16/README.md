# Starbase - Your Personal Code Repository Manager

Never lose track of your code again! Starbase centralizes all your scattered code into one searchable repository.

## Development & Release Process

To release a new version to PyPI:

```bash
python release.py
```

That's it! This automatically:
- Increments the version
- Syncs starbase.py → src/starbase/cli.py with import fixes
- Builds the package with PDM
- Commits and tags the release
- Uploads to PyPI using ~/.pypirc credentials

After release, push to GitHub:
```bash
git push && git push --tags
```

## Quick Start

```bash
# If using PDM (recommended):
pdm run python menu.py

# Or activate the environment first:
pdm shell
python menu.py
```

That's it! The interactive menu will guide you through everything.

## What This Does

Starbase solves the "where did I put that code?" problem by:
- **Extracting** code from messy project folders with intelligent dependency detection
- **Storing** everything in a centralized repository at ~/starbase
- **Searching** your code using natural language (even with typos!)
- **Installing** any stored package instantly with PDM or pip

## First Time Setup

1. Install dependencies:
   ```bash
   pdm install
   # or
   pip install -r requirements.txt
   ```

2. Run the menu:
   ```bash
   pdm run python menu.py
   ```

3. Choose option 1 to extract your first project!

## Common Commands

```bash
# Using PDM (recommended way):
pdm run python menu.py                    # Interactive menu
pdm run python starbase.py extract .      # Extract current directory
pdm run python starbase.py search "term"  # Search for code

# Or activate environment once and run directly:
pdm shell                                  # Activates the virtual environment
python menu.py                            # Now you can run directly
python starbase.py extract .
```

## Key Features

- 🤖 **AI-Powered**: Automatically generates descriptions and understands natural language searches
- 📦 **Smart Extraction**: Detects entry points and traces all dependencies
- 🔍 **Semantic Search**: Find code even when you can't remember exact names
- 💻 **Claude Integration**: Your code automatically available to Claude Desktop (MCP)
- ⚡ **Zero Config**: Works out of the box with intelligent defaults

## Requirements
- Python 3.8+
- PDM or pip
- Optional: Groq/Claude API key for AI features

## MCP Server Integration (Claude, VSCode, Copilot)

Starbase automatically configures itself as an MCP server on first run, making your code available to AI assistants everywhere!

### 🚀 Auto-Configuration
When you run `starbase` for the first time, it automatically:
- ✅ Installs MCP server globally
- ✅ Configures Claude Desktop
- ✅ Configures Claude Code CLI  
- ✅ Creates VSCode-compatible wrapper

### 📝 VSCode/GitHub Copilot Setup

If VSCode doesn't detect the MCP server automatically:

1. **Reload VSCode** (if you had errors before):
   - Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
   - Type: "Developer: Reload Window"

2. **Check MCP Server Status**:
   - Open Output panel (`View` → `Output`)
   - Select "MCP" from dropdown
   - Should show "Starting server starbase"

3. **Manually Add/Restart Server**:
   - Press `Cmd+Shift+P` / `Ctrl+Shift+P`
   - Type: "MCP: Restart Server" or "MCP: Add Server"
   - Select "starbase"

4. **Manual Configuration** (if needed):
   - Command: `python starbase_mcp_server.py`
   - Type: `stdio`

### 🤖 Claude Desktop
After running `starbase` once, restart Claude Desktop. You'll see:
- 🔌 **starbase** tool available in Claude
- Can search and retrieve any extracted code

### 🛠️ Available MCP Commands
Once connected, AI assistants can:
- `search_packages("query")` - Search your code with natural language
- `get_package_code("name")` - Retrieve full source code
- `list_all_packages()` - See everything in your starbase
- `get_install_command("name")` - Get install instructions

### 🔧 Troubleshooting MCP

**VSCode Issues:**
- Make sure you have the MCP extension installed
- Check that `starbase_mcp_server.py` exists in your project root
- Try: `MCP: Restart Server` from command palette

**Claude Desktop Issues:**
- Check config at: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac)
- Should contain `starbase` in `mcpServers` section
- Restart Claude Desktop after any config changes

**Testing the Server:**
```bash
# Test if MCP server works
starbase-mcp-server --help

# Or with PDM
pdm run starbase-mcp-server
```

---
*Never lose code again. Never search through old folders. Just Starbase it!*
