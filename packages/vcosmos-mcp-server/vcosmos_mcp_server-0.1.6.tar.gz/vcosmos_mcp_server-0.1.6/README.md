# vCosmos UUT MCP Server

A Model Context Protocol (MCP) server that provides tools to query Units Under Test (UUTs) and tasks from the vCosmos Test Logic API.

📦 **Available on PyPI**: [vcosmos-mcp-server](https://pypi.org/project/vcosmos-mcp-server/)  
▶️ **Install & Run**:
```bash
uvx vcosmos-mcp-server
```

## 🚀 Quick Start

1. **Set your vCosmos token**:
   ```bash
   export VCOSMOS_TOKEN="your_token_here"   # Linux/Mac
   $env:VCOSMOS_TOKEN="your_token_here"     # PowerShell
   ```

2. **Run the server** (choose one option):

   - **Option A: Manual**  
     Run directly from command line:
     ```bash
     uvx vcosmos-mcp-server
     ```

   - **Option B: VS Code Integration (Recommended)**  
     Add this to your VS Code MCP settings:
     ```json
     {
       "mcpServers": {
         "vcosmos": {
           "command": "uvx",
           "args": ["vcosmos-mcp-server"],
           "env": {
             "VCOSMOS_TOKEN": "your_token_here"
           }
         }
       }
     }
     ```

## 🏗️ Architecture

![Architecture Diagram](https://raw.githubusercontent.com/<your-repo>/main/docs/architecture.png)

## 📖 Documentation

- [Usage Guide](https://github.com/<your-repo>/docs/usage.md)
- [API Reference](https://github.com/<your-repo>/docs/api.md)

---

**Package Name**: `vcosmos-mcp-server`  
**Python**: 3.8+  
**License**: MIT
