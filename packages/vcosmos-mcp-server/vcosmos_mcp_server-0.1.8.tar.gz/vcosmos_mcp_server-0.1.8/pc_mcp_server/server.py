#!/usr/bin/env python3
"""
PC Control MCP Server - Windows Theme Control

A simple MCP server for controlling Windows light/dark theme switching.

Usage:
1. Install dependencies: uv add mcp
2. Configure this script in VS Code's mcp.json
"""

import asyncio
import logging
import subprocess
import sys
from typing import Dict, List, Any

# MCP library imports
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("pc-mcp-server")


class WindowsThemeController:
    """Windows Theme Controller using PowerShell commands"""
    
    def __init__(self):
        self.light_theme_command = (
            'Set-ItemProperty -Path "HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" '
            '-Name "AppsUseLightTheme" -Value 1 -Type DWord; '
            'Set-ItemProperty -Path "HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" '
            '-Name "SystemUsesLightTheme" -Type DWord -Value 1'
        )
        self.dark_theme_command = (
            'Set-ItemProperty -Path "HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" '
            '-Name "AppsUseLightTheme" -Value 0 -Type DWord; '
            'Set-ItemProperty -Path "HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" '
            '-Name "SystemUsesLightTheme" -Type DWord -Value 0'
        )
        self.get_theme_command = (
            'Get-ItemProperty -Path "HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" '
            '-Name "AppsUseLightTheme", "SystemUsesLightTheme" | Select-Object AppsUseLightTheme, SystemUsesLightTheme'
        )
    
    def _run_powershell_command(self, command: str) -> tuple[bool, str]:
        """Execute PowerShell command and return (success, output)"""
        try:
            result = subprocess.run(
                ["pwsh.exe", "-Command", command],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                error_msg = result.stderr.strip() if result.stderr else f"Command failed with exit code {result.returncode}"
                logger.error(f"PowerShell command failed: {error_msg}")
                return False, error_msg
                
        except subprocess.TimeoutExpired:
            error_msg = "Command timed out"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Failed to execute command: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def set_light_theme(self) -> tuple[bool, str]:
        """Switch to light theme"""
        logger.info("Switching to light theme")
        return self._run_powershell_command(self.light_theme_command)
    
    def set_dark_theme(self) -> tuple[bool, str]:
        """Switch to dark theme"""
        logger.info("Switching to dark theme")
        return self._run_powershell_command(self.dark_theme_command)
    
    def get_current_theme(self) -> tuple[bool, str]:
        """Get current theme status"""
        logger.info("Getting current theme status")
        return self._run_powershell_command(self.get_theme_command)


# Create MCP server instance
server = Server("pc-mcp-server")
theme_controller = WindowsThemeController()


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="set_windows_theme",
            description="Switch Windows system theme between light and dark mode",
            inputSchema={
                "type": "object",
                "properties": {
                    "theme": {
                        "type": "string",
                        "description": "Theme to switch to",
                        "enum": ["light", "dark"]
                    }
                },
                "required": ["theme"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="get_windows_theme",
            description="Get current Windows theme status (light or dark)",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls"""
    try:
        if name == "set_windows_theme":
            return await set_windows_theme_handler(arguments)
        elif name == "get_windows_theme":
            return await get_windows_theme_handler(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        return [TextContent(type="text", text=f"Tool execution error: {str(e)}")]


async def set_windows_theme_handler(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle theme switching"""
    theme = arguments.get("theme")
    
    if theme not in ["light", "dark"]:
        return [TextContent(
            type="text", 
            text=f"Error: theme must be 'light' or 'dark', got: {theme}"
        )]
    
    if theme == "light":
        success, output = theme_controller.set_light_theme()
    else:
        success, output = theme_controller.set_dark_theme()
    
    if success:
        return [TextContent(
            type="text", 
            text=f"Successfully switched to {theme} theme. Changes may require explorer restart to take full effect."
        )]
    else:
        return [TextContent(
            type="text", 
            text=f"Failed to switch to {theme} theme: {output}"
        )]


async def get_windows_theme_handler(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle getting current theme status"""
    success, output = theme_controller.get_current_theme()
    
    if success:
        # Parse the PowerShell output to determine current theme
        if "AppsUseLightTheme" in output and "SystemUsesLightTheme" in output:
            lines = output.split('\n')
            apps_light = None
            system_light = None
            
            for line in lines:
                if "AppsUseLightTheme" in line and "SystemUsesLightTheme" in line:
                    # This might be the header line, skip it
                    continue
                elif line.strip() and not line.startswith('-'):
                    # This should be the data line
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            apps_light = int(parts[0])
                            system_light = int(parts[1])
                            break
                        except (ValueError, IndexError):
                            continue
            
            if apps_light is not None and system_light is not None:
                if apps_light == 1 and system_light == 1:
                    current_theme = "light"
                elif apps_light == 0 and system_light == 0:
                    current_theme = "dark"
                else:
                    current_theme = f"mixed (Apps: {'light' if apps_light == 1 else 'dark'}, System: {'light' if system_light == 1 else 'dark'})"
                
                return [TextContent(
                    type="text", 
                    text=f"Current Windows theme: {current_theme}\n\nRaw output:\n{output}"
                )]
        
        return [TextContent(
            type="text", 
            text=f"Theme status retrieved but format unexpected:\n{output}"
        )]
    else:
        return [TextContent(
            type="text", 
            text=f"Failed to get theme status: {output}"
        )]


async def main():
    """Main entry point - using MCP library stdio server"""
    logger.info("Starting PC MCP Server (Windows Theme Control)")
    
    # Check if we're on Windows
    if sys.platform != "win32":
        logger.warning("This server is designed for Windows only")
    
    # Use MCP library stdio server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


def cli():
    """Sync entrypoint for console_scripts."""
    asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())
