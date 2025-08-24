# vCosmos UUT MCP Server

A Model Context Protocol (MCP) server that provides tools to query Units Under Test (UUTs) and tasks from the vCosmos Test Logic API using the official MCP Python library.

**📦 Now available as a PyPI package!** Install and run with: `uvx vcosmos-mcp-server`

## 🎯 Overview

This production-ready, packaged MCP server exposes vCosmos API functionality to MCP clients (like VS Code, Claude, etc.), allowing them to:

- Query UUTs with comprehensive filtering options (pool, site, status, product, health, etc.)
- Query vCosmos tasks with filtering and sorting capabilities
- Get data in optimized flat JSON format for LLM consumption
- Support for sorting and pagination

## 🏗️ Architecture

```mermaid
graph TD
    A[MCP Client<br/>VS Code, Claude, etc.] -->|MCP Protocol<br/>JSON-RPC over stdio| B[vCosmos MCP Server]
    
    subgraph B[vCosmos MCP Server]
        C[MCP Tools<br/>• query_vcosmos_uuts<br/>• query_vcosmos_tasks]
        D[VCosmosAPIClient Class<br/>built-in HTTP client]
    end
    
    B -->|HTTPS/REST| E[vCosmos Test Logic API]
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#fff3e0
    style D fill:#fff3e0
    style E fill:#e8f5e8
```

## 🔧 Available Tools

### `query_vcosmos_uuts`

Query vCosmos test devices (UUT) with comprehensive filtering and sorting options.

**Parameters:**
- `pool` (optional): Device pool ID
- `id` (optional): UUT ID  
- `site` (optional): Site name
- `ip` (optional): IP address
- `status` (optional): Device status
- `internal_product_name` (optional): Internal product name
- `marketing_product_name` (optional): Marketing product name
- `phase` (optional): Product phase
- `release_year` (optional): Release year
- `limit` (optional, default: 25): Return result count limit (1-5000)
- `health_status` (optional): Health status (Healthy, Unhealthy, Offline, Unregistered)
- `sort_by` (optional, default: "id"): Sort field
- `sort_direction` (optional, default: "asc"): Sort direction (asc, desc)

**Returns:**
- Flat JSON array of UUT objects with fields like: id, hostname, serial_number, site, ip_address, status, product_name, health_status, etc.

### `query_vcosmos_tasks`

Query vCosmos tasks with filtering and sorting capabilities.

**Parameters:**
- `status` (optional): Task status filter (Waiting, Pending, Running, Done, etc.)
- `result_status` (optional): Result status filter (PASS, FAIL, None, etc.)
- `site` (optional): Site name filter
- `job_id` (optional): Job ID filter
- `executor` (optional): Executor filter
- `uut_serial_number` (optional): UUT serial number filter
- `limit` (optional, default: 25): Task count limit (1-50)
- `sort_by` (optional, default: "createdAt"): Sort field
- `sort_direction` (optional, default: "desc"): Sort direction (asc, desc)

**Returns:**
- Flat JSON array of task objects with fields like: id, job_id, status, result_status, finished_at, uut_serial_number

## 🚀 Quick Start

### Prerequisites

Before using this MCP server, ensure you have the following installed:

- **Python 3.8+**: Download from [python.org](https://www.python.org/downloads/)
- **uv**: Python package installer and resolver. Install from [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/)
- **Valid vCosmos authentication token**: Contact your vCosmos administrator

### Installation (Recommended: uvx)

The easiest way to install and run the vCosmos MCP server is using `uvx`:

1. **Install and run with uvx (one command):**
   ```bash
   uvx vcosmos-mcp-server
   ```

   This automatically:
   - Downloads and installs the package from PyPI
   - Sets up an isolated environment
   - Runs the MCP server

2. **Set your authentication token:**
   ```powershell
   # PowerShell
   $env:VCOSMOS_TOKEN = "your_token_here"
   
   # Linux/Mac
   export VCOSMOS_TOKEN="your_token_here"
   ```

### Alternative Installation Methods

#### Method 1: Install with uv
```bash
# Install the package
uv add vcosmos-mcp-server

# Run the server
vcosmos-mcp-server
```

#### Method 2: Development Installation
For development or customization:

```bash
# Clone the repository
git clone <repository-url>
cd vcosmos-mcp-server

# Install dependencies
uv sync

# Run the server
uv run vcosmos-mcp-server
```

### VS Code Integration

#### Option 1: Using uvx (Recommended)

Add this configuration to your VS Code MCP settings:

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

#### Option 2: Development/Local

For development or local installations:

```json
{
  "mcpServers": {
    "vcosmos": {
      "command": "python",
      "args": ["project_file_path/vcosmos_mcp_server/server.py"],
      "env": {
        "VCOSMOS_TOKEN": "your_token_here"
      }
    }
  }
}
```

## 📋 Current Implementation

The current implementation is a **production-ready, packaged MCP server** available on PyPI that includes:

- ✅ **PyPI Package**: Published as `vcosmos-mcp-server` for easy installation
- ✅ **uvx Compatible**: Can be run directly with `uvx vcosmos-mcp-server`
- ✅ **Official MCP Library**: Uses the official MCP Python library
- ✅ **Async Implementation**: Full async/await support
- ✅ **stdio Transport**: JSON-RPC over stdio communication
- ✅ **Two Main Tools**: `query_vcosmos_uuts` and `query_vcosmos_tasks`
- ✅ **Comprehensive Filtering**: Multiple filter options for both UUTs and tasks
- ✅ **Flat JSON Output**: Optimized for LLM consumption
- ✅ **Error Handling**: Robust error handling and validation
- ✅ **Built-in HTTP Client**: No external dependencies except MCP library
- ✅ **CLI Entry Point**: Includes `vcosmos-mcp-server` command

### Example Usage

Query UUTs by site:
```json
{
  "tool": "query_vcosmos_uuts",
  "arguments": {
    "site": "hp-tnn-prd",
    "limit": 10,
    "health_status": "Healthy"
  }
}
```

Query recent failed tasks:
```json
{
  "tool": "query_vcosmos_tasks", 
  "arguments": {
    "result_status": "FAIL",
    "limit": 5,
    "sort_by": "createdAt",
    "sort_direction": "desc"
  }
}
```

## 🔮 Features

### UUT Query Features
- Filter by pool, site, IP, status, product names, phase, release year
- Health status filtering (Healthy, Unhealthy, Offline, Unregistered)
- Sorting by various fields (id, site, ip, status, etc.)
- Pagination with configurable limits (1-5000)
- Flat JSON output with clean field names

### Task Query Features  
- Filter by status, result status, site, job ID, executor
- UUT serial number filtering
- Sort by creation date, status, executor, etc.
- Pagination with configurable limits (1-50)
- Extracts UUT serial numbers and result statuses

### Data Format
All responses are in flat JSON format optimized for LLM processing:

**UUT Response Example:**
```json
[
  {
    "id": "6710bdbdf3e08f001a43b627",
    "hostname": "test-hostname",
    "serial_number": "8CC1180BC4", 
    "site": "hp-tnn-prd",
    "ip_address": "15.37.194.115",
    "status": "Idle",
    "product_name": "HP EliteDesk 800 G8",
    "health_status": "Healthy",
    "last_updated": "2025-08-22T13:45:54.377Z"
  }
]
```

**Task Response Example:**
```json
[
  {
    "id": "68a955a3a5e663f2cca2e788",
    "job_id": "job123",
    "status": "Running", 
    "result_status": "PASS",
    "finished_at": "2025-08-23T10:30:00Z",
    "uut_serial_number": "000277072S"
  }
]
```

## � Package Information

- **Package Name**: `vcosmos-mcp-server`
- **Latest Version**: `0.1.5`
- **Python Support**: 3.8+
- **PyPI**: [https://pypi.org/project/vcosmos-mcp-server/](https://pypi.org/project/vcosmos-mcp-server/)
- **Installation**: `uvx vcosmos-mcp-server` (recommended)
- **CLI Command**: `vcosmos-mcp-server`
- **Dependencies**: Only requires `mcp>=1.13.1`

## �📁 File Structure

```
vcosmos-mcp-server/
├── vcosmos_mcp_server/           # 📦 Main package directory
│   ├── __init__.py              # Package initialization
│   └── server.py                # ✅ Production MCP Server (main module)
├── pyproject.toml               # 📦 Package configuration and dependencies
├── README.md                    # 📖 Main project documentation
├── LICENSE                      # 📄 MIT License
├── MANIFEST.in                  # 📦 Package manifest
└── uv.lock                      # 🔒 Dependency lock file
```

**PyPI Package**: Available as `vcosmos-mcp-server` on [PyPI](https://pypi.org/project/vcosmos-mcp-server/)
**CLI Command**: `vcosmos-mcp-server` (automatically available after installation)

## 🧪 Testing the Server

You can test the server functionality using different methods:

### Method 1: Using uvx (Recommended)
```bash
# Set your token
export VCOSMOS_TOKEN="your_token_here"  # Linux/Mac
# or
$env:VCOSMOS_TOKEN = "your_token_here"   # PowerShell

# Run and test the server
uvx vcosmos-mcp-server

# The server will show:
# INFO - Starting vCosmos MCP Server
# INFO - VCOSMOS_TOKEN configured
# INFO - Server ready for MCP connections
```

### Method 2: Using installed package
```bash
# Install first
uv add vcosmos-mcp-server

# Run the server
vcosmos-mcp-server
```

### Method 3: Development testing
```bash
# From the project directory
uv run vcosmos-mcp-server
```

For integration testing with MCP clients, configure the server in your MCP client and test the tools through the client interface.

## 🎯 Integration with MCP Clients

This server is ready for integration with:

- **VS Code**: Through MCP extensions and settings configuration
- **Claude**: Through MCP protocol support  
- **Custom Applications**: Any application supporting the MCP standard

## 🔒 Security Notes

- The server uses the `VCOSMOS_TOKEN` environment variable for authentication
- Built-in HTTP client with proper timeout handling (30 seconds)
- No credentials are stored in the code
- All API communication uses HTTPS

## 🐛 Troubleshooting

1. **"VCOSMOS_TOKEN environment variable not set"**: 
   - Set the environment variable with your vCosmos API token
   - Verify the token has the correct permissions

2. **"Request error" or API failures**:
   - Check your network connection to vcosmos.hpcloud.hp.com
   - Verify your token is valid and not expired
   - Check if the vCosmos API endpoints are accessible

3. **"Tool execution error"**:
   - Check the server logs for detailed error messages
   - Validate your tool parameters match the schema
   - Ensure limit values are within the allowed ranges

4. **Empty results `[]`**:
   - Check if there are UUTs/tasks matching your filter criteria
   - Try broader filter parameters or remove filters to see all data
   - Verify your token has access to the requested site/pool

## ⚡ Performance Notes

- UUT queries support up to 5000 results per request
- Task queries support up to 50 results per request  
- Built-in request timeout of 30 seconds
- Flat JSON output optimized for LLM token efficiency
- Minimal memory footprint with direct field extraction

This production-ready MCP server provides a robust bridge between your vCosmos infrastructure and AI/automation tools! 🚀
