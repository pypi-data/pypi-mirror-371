# src/servicenow_mcp_server/analytics/analytics_tools.py

"""
This module defines tools for Reporting and Analytics, using ServiceNow's
Aggregate API.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from fastmcp import FastMCP
from servicenow_mcp_server.utils import ServiceNowClient

# Local MCP instance for decorating tools
mcp = FastMCP()

def register_tools(mcp: FastMCP):
    """Adds all tools defined in this file to the main server's MCP instance."""
    mcp.add_tool(get_aggregate_data)

# ==============================================================================
#  Pydantic Models
# ==============================================================================

class BaseToolParams(BaseModel):
    instance_url: str = Field(..., description="The full URL of the ServiceNow instance.")
    username: str = Field(..., description="The username for authentication.")
    password: str = Field(..., description="The password for authentication.", sensitive=True)

class GetAggregateDataParams(BaseToolParams):
    table_name: str = Field(..., description="The table to perform the aggregation on (e.g., 'incident').")
    aggregation_function: str = Field(..., description="The aggregation function to use (e.g., 'COUNT', 'AVG', 'SUM', 'MIN', 'MAX').")
    field_to_aggregate: Optional[str] = Field(None, description="The field to apply the function to (required for AVG, SUM, etc., but not for COUNT).")
    group_by_fields: Optional[List[str]] = Field(None, description="A list of fields to group the results by (e.g., ['priority', 'state']).")
    query: Optional[str] = Field(None, description="An optional ServiceNow encoded query to filter the records before aggregating.")

# ==============================================================================
#  Tool Functions
# ==============================================================================

@mcp.tool()
async def get_aggregate_data(params: GetAggregateDataParams) -> Dict[str, Any]:
    """
    Performs an aggregation (COUNT, AVG, SUM, etc.) on a table, with optional grouping.
    This is powerful for real-time statistics.
    """
    async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
        # This tool uses the special 'stats' endpoint, not the 'table' endpoint.
        endpoint = f"/api/now/stats/{params.table_name}"
        
        query_params = {
            "sysparm_count": "true", # Using COUNT as a base, but the function parameter will override
            "sysparm_query": params.query or "",
            "sysparm_aggr_fields": params.field_to_aggregate or "", # Field for AVG/SUM
            "sysparm_group_by": ",".join(params.group_by_fields) if params.group_by_fields else "",
            "sysparm_aggregation": params.aggregation_function # The main function
        }

        return await client.send_request("GET", endpoint, params=query_params)