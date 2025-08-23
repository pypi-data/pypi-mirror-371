#!/usr/bin/env python3
"""MCP Server Auto-Installer for Starbase"""

import os
import shutil
import subprocess
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Optional imports for functionality moved from starbase.py
try:
    import toml
except ImportError:
    toml = None

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.prompt import Prompt, Confirm
except ImportError:
    Console, Panel, Syntax, Prompt, Confirm = None, None, None, None, None

console = Console() if Console else None

class MCPInstaller:
    """Handles MCP server installation and configuration for starbase."""

    def __init__(self, project_root_path: Optional[Path] = None):
        """
        Args:
            project_root_path: Path to the root of the starbase project source code.
        """
        self.project_root_path = Path(project_root_path) if project_root_path else Path.cwd()

    def is_globally_installed(self) -> bool:
        """Check if the 'starbase' command is available in the system's PATH."""
        return shutil.which("starbase") is not None
    
    def _cleanup_broken_installations(self, package_name: str):
        """Remove any broken or old installations of the package."""
        if package_name != "starbase":
            return  # Only cleanup starbase for now
        
        console.print("\n[cyan]🧹 Checking for old or broken installations...[/cyan]")
        
        # Check for pipx installation
        pipx_path = shutil.which("pipx")
        if pipx_path:
            try:
                # Check if starbase is installed via pipx
                result = subprocess.run([pipx_path, "list"], capture_output=True, text=True)
                if "starbase-code" in result.stdout:
                    console.print("[yellow]Found existing pipx installation. Removing...[/yellow]")
                    subprocess.run([pipx_path, "uninstall", "starbase-code"], capture_output=True)
                    console.print("[green]✓ Removed old pipx installation[/green]")
            except:
                pass  # Ignore errors during cleanup
        
        # Don't mention symlinks here - we'll handle them after installation
    
    def _ensure_standard_path_access(self, package_name: str):
        """Ensure the command is accessible in standard paths for Claude Desktop."""
        if package_name != "starbase":
            return
        
        # Check if Claude Desktop is installed
        claude_desktop_exists = False
        if sys.platform == "darwin":
            claude_desktop_exists = Path("/Applications/Claude.app").exists()
        elif sys.platform == "win32":
            # Check common Windows install locations
            import winreg
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Anthropic\Claude") as key:
                    claude_desktop_exists = True
            except:
                claude_desktop_exists = Path(os.environ.get("PROGRAMFILES", "") + r"\Claude\Claude.exe").exists()
        
        if not claude_desktop_exists:
            # Claude Desktop not installed, skip this step
            return
        
        console.print("\n[cyan]🔗 Claude Desktop detected. Setting up integration...[/cyan]")
        
        # Find where starbase and starbase-mcp-server were installed
        starbase_path = shutil.which("starbase")
        mcp_server_path = shutil.which("starbase-mcp-server")
        
        if not starbase_path:
            console.print("[red]Warning: Could not find starbase in PATH after installation[/red]")
            return
        
        if not mcp_server_path:
            console.print("[red]Warning: Could not find starbase-mcp-server in PATH after installation[/red]")
            return
        
        # Check if they're already in a standard location
        standard_paths = ["/usr/local/bin", "/opt/homebrew/bin", "/usr/bin"]
        starbase_dir = Path(starbase_path).parent
        
        if str(starbase_dir) in standard_paths:
            console.print(f"[green]✓ Starbase already accessible to Claude Desktop at {starbase_path}[/green]")
            return
        
        # Create symlinks in /usr/local/bin for Claude Desktop
        # We need BOTH starbase and starbase-mcp-server
        symlinks_to_create = [
            (starbase_path, Path("/usr/local/bin/starbase")),
            (mcp_server_path, Path("/usr/local/bin/starbase-mcp-server"))
        ]
        
        console.print(f"[yellow]Creating symlinks for Claude Desktop integration...[/yellow]")
        
        symlink_failed = False
        created_symlinks = []
        
        for source_path, symlink_path in symlinks_to_create:
            console.print(f"[dim]Linking {source_path} → {symlink_path}[/dim]")
            
            try:
                # First try without sudo (unlikely to work but worth trying)
                symlink_path.unlink(missing_ok=True)
                symlink_path.symlink_to(source_path)
                console.print(f"[green]✓ Created symlink at {symlink_path}[/green]")
                created_symlinks.append(symlink_path)
            except PermissionError:
                # Need sudo - try with sudo
                if not symlink_failed:  # Only show this message once
                    console.print("[yellow]Administrator access required for Claude Desktop integration.[/yellow]")
                    console.print("[dim]You may be prompted for your password.[/dim]")
                
                try:
                    # Remove old symlink if it exists
                    subprocess.run(["sudo", "rm", "-f", str(symlink_path)], capture_output=True)
                    # Create new symlink
                    result = subprocess.run(
                        ["sudo", "ln", "-sf", str(source_path), str(symlink_path)],
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode == 0:
                        console.print(f"[green]✓ Created symlink at {symlink_path}[/green]")
                        created_symlinks.append(symlink_path)
                    else:
                        console.print(f"[red]Failed to create symlink: {result.stderr}[/red]")
                        symlink_failed = True
                except Exception as e:
                    console.print(f"[red]Error running sudo: {e}[/red]")
                    symlink_failed = True
        
        if created_symlinks and not symlink_failed:
            console.print("[green]✓ Claude Desktop integration complete![/green]")
            console.print("[dim]Restart Claude Desktop to use the starbase MCP server.[/dim]")
        elif symlink_failed:
            console.print("\n[yellow]To complete Claude Desktop integration manually, run:[/yellow]")
            for source_path, symlink_path in symlinks_to_create:
                if symlink_path not in created_symlinks:
                    console.print(f"[cyan]sudo ln -sf {source_path} {symlink_path}[/cyan]")
            
            # Also update Claude config to use full path as fallback
            console.print("\n[yellow]Alternatively, updating Claude Desktop config to use full path...[/yellow]")
            self._update_claude_desktop_config_with_full_path(mcp_server_path)
    
    def _update_claude_desktop_config_with_full_path(self, mcp_server_path: str):
        """Update Claude Desktop config to use full path if symlink creation fails."""
        config_path = self._get_claude_desktop_config_path()
        if not config_path.exists():
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config = {"mcpServers": {}}
        else:
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
            except json.JSONDecodeError:
                config = {"mcpServers": {}}
        
        if "mcpServers" not in config:
            config["mcpServers"] = {}
        
        # Use full path to starbase-mcp-server
        starbase_config = {
            "command": str(mcp_server_path),
            "args": []
        }
        
        config["mcpServers"]["starbase"] = starbase_config
        
        try:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            console.print(f"[green]✓ Updated Claude Desktop config to use full path: {mcp_server_path}[/green]")
            console.print("[dim]This approach works but may break if you reinstall starbase to a different location.[/dim]")
            return True
        except Exception as e:
            console.print(f"[red]Error updating Claude Desktop config: {e}[/red]")
            return False

    def install_and_configure_mcp(self, package_name: str = "starbase") -> bool:
        """
        Main function to perform a full global installation and MCP configuration.
        """
        if not console:
            print("Rich console components not available. Please run 'pip install rich'.")
            return False
            
        console.print(f"\n[cyan]🚀 Starting global installation and MCP configuration for '{package_name}'...[/cyan]")

        # Step 0: Clean up any broken installations first
        self._cleanup_broken_installations(package_name)

        # Step 1: Install the package globally
        install_success = self._install_package_globally(package_name)
        if not install_success:
            console.print(f"[red]❌ Global installation for '{package_name}' failed. Aborting MCP configuration.[/red]")
            return False
        
        console.print(f"[green]✓ '{package_name}' package installed successfully.[/green]")

        # Step 1.5: Ensure starbase is accessible in standard paths for Claude Desktop
        self._ensure_standard_path_access(package_name)

        # Step 2: Configure Claude clients to use the new MCP server
        console.print("\n[cyan]⚙️  Configuring Claude clients for MCP access...[/cyan]")
        desktop_updated = self._update_claude_config()
        cli_updated = self._update_claude_code_config()

        if desktop_updated or cli_updated:
            console.print("\n[green]✓ Claude Desktop and/or Claude Code CLI configurations updated.[/green]")
            console.print("[dim]Restart Claude clients to see the changes.[/dim]")
        else:
            console.print("\n[dim]Claude configurations already up to date.[/dim]")
        
        console.print("\n[bold green]✅ Starbase installation and MCP configuration complete![/bold green]")
        return True

    def _prepare_package_for_global_install(self, package_path: Path, package_name: str) -> bool:
        """Prepares a package for global installation by ensuring proper configuration."""
        pyproject_path = self.project_root_path / "pyproject.toml"
        
        if not toml:
            console.print("[red]TOML library not found. Please run 'pip install toml'.[/red]")
            return False
            
        if not pyproject_path.exists():
            console.print(f"[red]No pyproject.toml found at {pyproject_path}[/red]")
            return False

        try:
            pyproject_data = toml.load(pyproject_path)
        except Exception as e:
            console.print(f"[red]Error reading pyproject.toml: {e}[/red]")
            return False

        if "project" not in pyproject_data:
            console.print("[red]Invalid pyproject.toml: missing [project] section[/red]")
            return False

        # Ensure console scripts are defined for the main 'starbase' package
        if package_name == "starbase" and "scripts" not in pyproject_data.get("project", {}):
            console.print("[yellow]Adding missing console script entry for 'starbase' to pyproject.toml[/yellow]")
            pyproject_data["project"]["scripts"] = {"starbase": "starbase:app"}
            with open(pyproject_path, 'w') as f:
                toml.dump(pyproject_data, f)
        
        return True

    def _install_package_globally(self, package_name: str, method: str = "auto") -> bool:
        """
        Install starbase-code from PyPI using pipx.
        """
        console.print(f"\n[cyan]Installing '{package_name}' from PyPI...[/cyan]")

        # 1. Try pipx
        pipx_path = shutil.which("pipx")
        if pipx_path:
            console.print("\n[cyan]🚀 Installing from PyPI with pipx...[/cyan]")
            try:
                # Install from PyPI
                pipx_command = [pipx_path, "install", "--force", "starbase-code"]
                subprocess.run(pipx_command, check=True, capture_output=True, text=True)
                console.print("[bold green]✅ Success! Starbase installed globally via pipx.[/bold green]")
                console.print("[dim]Please restart your terminal for changes to take effect.[/dim]")
                return True
            except subprocess.CalledProcessError as e:
                console.print(f"[red]❌ pipx installation failed: {e.stderr}[/red]")
                return False
        else:
            console.print("[red]❌ pipx not found. Install pipx first:[/red]")
            console.print("  macOS: [cyan]brew install pipx[/cyan]")
            console.print("  Linux: [cyan]sudo apt install pipx[/cyan]")
            console.print("  Or:    [cyan]python3 -m pip install --user pipx[/cyan]")
            return False

    def configure_project_mcp(self, project_path: Optional[Path] = None) -> bool:
        """Configure starbase MCP server for a specific Claude Code project."""
        project_path = Path(project_path) if project_path else Path.cwd()
        mcp_config_path = project_path / ".mcp.json"
        
        config = {"mcpServers": {}}
        if mcp_config_path.exists():
            try:
                with open(mcp_config_path, 'r') as f:
                    config = json.load(f)
                    if "mcpServers" not in config:
                        config["mcpServers"] = {}
            except json.JSONDecodeError:
                config = {"mcpServers": {}}

        starbase_config = {
            "type": "stdio",
            "command": "starbase",
            "args": ["mcp-server"]
        }

        if "starbase" in config.get("mcpServers", {}) and config["mcpServers"]["starbase"] == starbase_config:
            console.print("[dim]Starbase MCP server already configured for this project.[/dim]")
            return True

        config["mcpServers"]["starbase"] = starbase_config
        
        try:
            with open(mcp_config_path, 'w') as f:
                json.dump(config, f, indent=2)
            console.print(f"\n[green]✓ Configured starbase MCP server for project: {project_path}[/green]")
            return True
        except Exception as e:
            console.print(f"[red]Error configuring project MCP: {e}[/red]")
            return False

    def _get_claude_desktop_config_path(self) -> Path:
        if sys.platform == "darwin":
            return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
        elif sys.platform == "win32":
            return Path(os.environ.get("APPDATA", "")) / "Claude" / "claude_desktop_config.json"
        else:
            return Path.home() / ".config" / "Claude" / "claude_desktop_config.json"

    def _ensure_claude_config_exists(self) -> Dict[str, Any]:
        config_path = self._get_claude_desktop_config_path()
        config_path.parent.mkdir(parents=True, exist_ok=True)
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def _update_claude_config(self) -> bool:
        """Update Claude Desktop config to use the global 'starbase mcp-server' command."""
        config = self._ensure_claude_config_exists()
        config_path = self._get_claude_desktop_config_path()
        
        if "mcpServers" not in config:
            config["mcpServers"] = {}
        
        # Use the dedicated starbase-mcp-server command
        starbase_config = {
            "command": "starbase-mcp-server",
            "args": []
        }
        
        if "starbase" in config.get("mcpServers", {}) and config["mcpServers"]["starbase"] == starbase_config:
            return False

        config["mcpServers"]["starbase"] = starbase_config
        
        try:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            console.print(f"[red]Error updating Claude Desktop config: {e}[/red]")
            return False

    def _get_claude_code_config_path(self) -> Path:
        return Path.home() / ".claude.json"

    def _update_claude_code_config(self) -> bool:
        """Update Claude Code CLI config to use the global 'starbase mcp-server' command."""
        config_path = self._get_claude_code_config_path()
        config = {}
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
            except json.JSONDecodeError:
                config = {}

        if "mcpServers" not in config:
            config["mcpServers"] = {}
            
        # Use the dedicated starbase-mcp-server command  
        starbase_config = {
            "type": "stdio",
            "command": "starbase-mcp-server",
            "args": []
        }

        if "starbase" in config.get("mcpServers", {}) and config["mcpServers"]["starbase"] == starbase_config:
            return False

        config["mcpServers"]["starbase"] = starbase_config
        
        try:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            console.print(f"[red]Error updating Claude Code config: {e}[/red]")
            return False