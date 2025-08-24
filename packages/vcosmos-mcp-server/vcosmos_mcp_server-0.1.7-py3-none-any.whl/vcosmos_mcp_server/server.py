#!/usr/bin/env python3
"""
vCosmos UUT MCP Server - Using Official MCP Library

Usage:
1. Install dependencies: uv add mcp
2. Set environment variable VCOSMOS_TOKEN
3. Configure this script in VS Code's mcp.json
"""

import asyncio
import os
import logging
from typing import Dict, List, Any, Optional
import urllib.request
import urllib.parse
import json

# MCP library imports
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("vcosmos-mcp-server")


class VCosmosAPIClient:
    """
    vCosmos API Client - Using standard library
    """
    
    def __init__(self, base_url: str = "https://vcosmos.hpcloud.hp.com/api/tl"):
        self.base_url = base_url.rstrip('/')
        self.auth_token = os.getenv('VCOSMOS_TOKEN')
        
        if not self.auth_token:
            logger.warning("VCOSMOS_TOKEN environment variable not set")
    
    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make HTTP request"""
        try:
            url = f"{self.base_url}{endpoint}"
            if params:
                query_params = {k: str(v) for k, v in params.items() if v is not None}
                if query_params:
                    url += '?' + urllib.parse.urlencode(query_params)
            
            req = urllib.request.Request(url)
            req.add_header('Content-Type', 'application/json')
            req.add_header('User-Agent', 'vCosmos-MCP-Server/2.0')
            
            if self.auth_token:
                req.add_header('Authorization', self.auth_token)
            
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status == 200:
                    data = response.read().decode('utf-8')
                    return json.loads(data)
                else:
                    logger.error(f"HTTP error: {response.status}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Request error: {e}")
            return {}
    
    def _parse_response_data(self, response: Dict[str, Any]) -> tuple[List[Dict[str, Any]], int]:
        """Unified API response data parsing, returns (data list, total count)"""
        if not response:
            return [], 0
        
        # Known response format: {"total": ..., "data": [...]}
        if isinstance(response, dict) and 'data' in response:
            data = response['data'] or []
            total_count = response.get('total', len(data))
            return data, total_count
        
        # Other cases return empty
        return [], 0
    
    def get_uuts(self, 
                 pool: Optional[str] = None,
                 id: Optional[str] = None,
                 site: Optional[str] = None,
                 ip: Optional[str] = None,
                 status: Optional[str] = None,
                 internal_product_name: Optional[str] = None,
                 marketing_product_name: Optional[str] = None,
                 phase: Optional[str] = None,
                 release_year: Optional[str] = None,
                 limit: int = 25,
                 health_status: Optional[str] = None) -> tuple[List[Dict[str, Any]], int]:
        """Get UUT list, returns (UUT list, total count)"""
        # Basic parameters (with defaults or required parameters)
        params = {
            'limit': min(limit, 5000) if limit else 25
        }
        
        # Filter parameters (optional parameters, only add when not empty)
        filter_params: Dict[str, Any] = {
            'pool': pool,
            'id': id,
            'site': site,
            'ip': ip,
            'status': status,
            'internalProductName': internal_product_name,
            'marketingProductName': marketing_product_name,
            'phase': phase,
            'releaseYear': release_year,
            'healthStatus': health_status
        }
        
        # Only add non-None filter parameters
        for key, value in filter_params.items():
            if value is not None:
                params[key] = value
        
        response = self._make_request('/uuts', params)
        return self._parse_response_data(response)
    
    def get_tasks(self, 
                  status: Optional[str] = None,
                  result_status: Optional[str] = None,
                  site: Optional[str] = None,
                  job_id: Optional[str] = None,
                  executor: Optional[str] = None,
                  uut_serial_number: Optional[str] = None,
                  limit: int = 25,
                  sort_by: str = "createdAt",
                  sort_direction: str = "desc") -> List[Dict[str, Any]]:
        """Query vCosmos tasks"""
        params = {
            'limit': min(limit, 50),
            'sortBy': sort_by,
            'sortDirection': sort_direction
        }
        
        # Add filter parameters
        filter_params = {
            'status': status,
            'resultStatus': result_status,
            'site': site,
            'jobId': job_id,
            'executor': executor,
            'uutSerialNumber': uut_serial_number
        }
        
        for key, value in filter_params.items():
            if value:
                params[key] = value
        
        response = self._make_request('/tasks', params)
        return self._parse_response_data(response)[0]


# Create MCP server instance
server = Server("vcosmos-mcp-server")
api_client = VCosmosAPIClient()


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="query_vcosmos_uuts",
            description="Query vCosmos test devices (UUT) with multiple filter conditions",
            inputSchema={
                "type": "object",
                "properties": {
                    "pool": {
                        "type": "string",
                        "description": "Device pool ID"
                    },
                    "id": {
                        "type": "string",
                        "description": "UUT ID"
                    },
                    "site": {
                        "type": "string",
                        "description": "Site name"
                    },
                    "ip": {
                        "type": "string",
                        "description": "IP address"
                    },
                    "status": {
                        "type": "string",
                        "description": "Device status"
                    },
                    "internal_product_name": {
                        "type": "string",
                        "description": "Internal product name"
                    },
                    "marketing_product_name": {
                        "type": "string",
                        "description": "Marketing product name"
                    },
                    "phase": {
                        "type": "string",
                        "description": "Product phase"
                    },
                    "release_year": {
                        "type": "string",
                        "description": "Release year"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Return result count limit",
                        "minimum": 1,
                        "maximum": 5000,
                        "default": 25
                    },
                    "health_status": {
                        "type": "string",
                        "description": "Health status",
                        "enum": ["Healthy", "Unhealthy", "Offline", "Unregistered"]
                    }
                },
                "additionalProperties": False
            }
        ),
        Tool(
            name="query_vcosmos_tasks",
            description="Query vCosmos tasks",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "Task status filter",
                        "enum": ["Waiting", "Pending", "Dispatching", "Started", "Running", "Cleaning", "Aborting", "Done", "Aborted", "Rejected"]
                    },
                    "result_status": {
                        "type": "string", 
                        "description": "Result status filter",
                        "enum": ["PASS", "FAIL", "None", "NA", "NS", "Other"]
                    },
                    "site": {
                        "type": "string",
                        "description": "Site name filter"
                    },
                    "job_id": {
                        "type": "string",
                        "description": "Job ID filter"
                    },
                    "executor": {
                        "type": "string",
                        "description": "Executor filter"
                    },
                    "uut_serial_number": {
                        "type": "string",
                        "description": "UUT serial number filter"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Task count limit",
                        "minimum": 1,
                        "maximum": 50,
                        "default": 25
                    },
                    "sort_by": {
                        "type": "string",
                        "description": "Sort field",
                        "enum": ["id", "site", "executor", "status", "createdAt"],
                        "default": "createdAt"
                    },
                    "sort_direction": {
                        "type": "string",
                        "description": "Sort direction",
                        "enum": ["asc", "desc"],
                        "default": "desc"
                    }
                },
                "additionalProperties": False
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls"""
    try:
        if name == "query_vcosmos_uuts":
            return await query_vcosmos_uuts_handler(arguments)
        elif name == "query_vcosmos_tasks":
            return await query_vcosmos_tasks_handler(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        return [TextContent(type="text", text=f"Tool execution error: {str(e)}")]


async def query_vcosmos_uuts_handler(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle UUT query"""
    # Extract parameters
    pool = arguments.get("pool")
    id = arguments.get("id")
    site = arguments.get("site")
    ip = arguments.get("ip")
    status = arguments.get("status")
    internal_product_name = arguments.get("internal_product_name")
    marketing_product_name = arguments.get("marketing_product_name")
    phase = arguments.get("phase")
    release_year = arguments.get("release_year")
    limit = arguments.get("limit", 25)
    health_status = arguments.get("health_status")
    
    if not isinstance(limit, int) or limit < 1 or limit > 5000:
        return [TextContent(
            type="text", 
            text=f"Error: limit must be an integer between 1-5000, got: {limit}"
        )]
    
    uuts, total_count = api_client.get_uuts(
        pool=pool,
        id=id,
        site=site,
        ip=ip,
        status=status,
        internal_product_name=internal_product_name,
        marketing_product_name=marketing_product_name,
        phase=phase,
        release_year=release_year,
        limit=limit,
        health_status=health_status,
    )
    
    if not uuts:
        return [TextContent(
            type="text", 
            text='[]'
        )]
    
    # Extract and format data for flat JSON output
    formatted_uuts = []
    for uut in uuts:
        if not isinstance(uut, dict):
            continue
        
        # Basic fields
        uut_id = uut.get('_id') or uut.get('id')
        
        # Configuration fields
        config = uut.get('configuration', {})
        hostname = config.get('hostName') if isinstance(config, dict) else None
        serial_number = config.get('serialNumber') if isinstance(config, dict) else None
        product_name = config.get('productName') if isinstance(config, dict) else None
        
        # Health status from health.status path
        health_status_value = uut.get('health', {}).get('status') if isinstance(uut.get('health'), dict) else None
        
        # Build JSON object with all fields (including optional ones)
        formatted_uut = {
            "id": uut_id,
            "hostname": hostname,
            "serial_number": serial_number,
            "site": uut.get('site'),
            "ip_address": uut.get('ip'),
            "status": uut.get('status'),
            "product_name": product_name,
            "health_status": health_status_value,
            "last_updated": uut.get('lastUpdated') or uut.get('updatedAt'),
            "internal_product": uut.get('internalProductName'),
            "marketing_product": uut.get('marketingProductName'),
            "phase": uut.get('phase'),
            "release_year": uut.get('releaseYear')
        }
        
        # Remove None values to keep JSON clean
        formatted_uut = {k: v for k, v in formatted_uut.items() if v is not None}
        formatted_uuts.append(formatted_uut)
    
    return [TextContent(type="text", text=json.dumps(formatted_uuts, indent=2))]


async def query_vcosmos_tasks_handler(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle task query"""
    # Extract parameters
    status = arguments.get("status")
    result_status = arguments.get("result_status")
    site = arguments.get("site")
    job_id = arguments.get("job_id")
    executor = arguments.get("executor")
    uut_serial_number = arguments.get("uut_serial_number")
    limit = arguments.get("limit", 25)
    sort_by = arguments.get("sort_by", "createdAt")
    sort_direction = arguments.get("sort_direction", "desc")
    
    if not isinstance(limit, int) or limit < 1 or limit > 50:
        return [TextContent(
            type="text", 
            text=f"Error: limit must be an integer between 1-50, got: {limit}"
        )]
    
    logger.info(f"Query {limit} tasks")
    
    tasks = api_client.get_tasks(
        status=status,
        result_status=result_status,
        site=site,
        job_id=job_id,
        executor=executor,
        uut_serial_number=uut_serial_number,
        limit=limit,
        sort_by=sort_by,
        sort_direction=sort_direction
    )
    
    if not tasks:
        return [TextContent(
            type="text", 
            text='[]'
        )]
    
    # Extract and format data for flat JSON output
    formatted_tasks = []
    for task in tasks:
        # UUT information from first UUT if available
        uut = task.get('uuts', [{}])[0] if task.get('uuts') else {}
        uut_serial = uut.get('serialNumber')  # Direct access based on API response structure
        
        # Result status from first action result if available
        result = task.get('result', {})
        result_status_value = None
        if result.get('uuts'):
            action_results = result['uuts'][0].get('actionResults', [])
            if action_results:
                result_status_value = action_results[0].get('status')
        
        # Build flat JSON object
        formatted_task = {
            "id": task.get('id'),
            "job_id": task.get('jobId'),
            "status": task.get('status'),
            "result_status": result_status_value,
            "finished_at": result.get('finishedAt'),
            "uut_serial_number": uut_serial
        }
        
        # Remove None values to keep JSON clean
        formatted_task = {k: v for k, v in formatted_task.items() if v is not None}
        formatted_tasks.append(formatted_task)
    
    return [TextContent(type="text", text=json.dumps(formatted_tasks, indent=2))]


async def main():
    """Main entry point - using MCP library stdio server"""
    logger.info("Starting vCosmos MCP Server (using MCP library)")
    
    # Check environment variables
    token = os.getenv('VCOSMOS_TOKEN')
    if not token:
        logger.warning("VCOSMOS_TOKEN environment variable not set")
    else:
        logger.info("VCOSMOS_TOKEN configured")
    
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