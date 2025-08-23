# src/servicenow_mcp_server/agile_management/epic_tools.py
"""
This module defines tools for interacting with Epics in ServiceNow's
Agile Development 2.0 application.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from fastmcp import FastMCP
from servicenow_mcp_server.utils import ServiceNowClient

# Local MCP instance for decorating tools in this file
mcp = FastMCP()

def register_tools(mcp: FastMCP):
    """Adds all tools defined in this file to the main server's MCP instance."""
    mcp.add_tool(create_epic)
    mcp.add_tool(update_epic)
    mcp.add_tool(list_epics)

# ==============================================================================
#  Pydantic Models
# ==============================================================================

class BaseToolParams(BaseModel):
    instance_url: str = Field(..., description="The full URL of the ServiceNow instance.")
    username: str = Field(..., description="The username for authentication.")
    password: str = Field(..., description="The password for authentication.", sensitive=True)

class CreateEpicParams(BaseToolParams):
    short_description: str = Field(..., description="A brief, one-line summary of the epic.")
    description: Optional[str] = Field(None, description="A detailed description of the epic.")
    parent: Optional[str] = Field(None, description="The sys_id of a parent epic, if this is a sub-epic.")
    theme: Optional[str] = Field(None, description="The sys_id of the theme this epic belongs to.")

class UpdateEpicParams(BaseToolParams):
    epic_id: str = Field(..., description="The sys_id of the epic to update.")
    short_description: Optional[str] = Field(None, description="A brief, one-line summary of the epic.")
    description: Optional[str] = Field(None, description="A detailed description of the epic.")
    parent: Optional[str] = Field(None, description="The sys_id of a parent epic, if this is a sub-epic.")
    theme: Optional[str] = Field(None, description="The sys_id of the theme this epic belongs to.")

class ListEpicsParams(BaseToolParams):
    limit: Optional[int] = Field(10, description="Maximum number of epics to return.")
    offset: Optional[int] = Field(0, description="Number of records to skip for pagination.")
    short_description: Optional[str] = Field(None, description="Filter by short description (LIKE search).")
    assigned_to: Optional[str] = Field(None, description="Filter by the sys_id of the assigned user.")
    state: Optional[str] = Field(None, description="Filter by state (e.g., 'New', 'In Progress', 'Done').")
    theme: Optional[str] = Field(None, description="Filter by the sys_id of the theme.")

# ==============================================================================
#  Tool Functions
# ==============================================================================

@mcp.tool()
async def create_epic(params: CreateEpicParams) -> Dict[str, Any]:
    """
    Creates a new epic in the Agile Development 2.0 module.
    """
    async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
        # The table for epics in Agile 2.0 is 'sn_agm_epic'.
        payload = params.model_dump(
            exclude={"instance_url", "username", "password"},
            exclude_unset=True
        )
        
        return await client.send_request("POST", "/api/now/table/rm_epic", data=payload)

@mcp.tool()
async def update_epic(params: UpdateEpicParams) -> Dict[str, Any]:
    """
    Updates an existing epic in the Agile Development 2.0 module.
    """
    async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
        payload = params.model_dump(
            exclude={"instance_url", "username", "password", "epic_id"},
            exclude_unset=True
        )
        
        return await client.send_request("PUT", f"/api/now/table/rm_epic/{params.epic_id}", data=payload)

@mcp.tool()
async def list_epics(params: ListEpicsParams) -> Dict[str, Any]:
    """
    Lists epics from ServiceNow with filtering options.
    """
    async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
        query_parts = []
        
        if params.short_description:
            query_parts.append(f"short_descriptionLIKE{params.short_description}")
        if params.assigned_to:
            query_parts.append(f"assigned_to={params.assigned_to}")
        if params.state:
            query_parts.append(f"state={params.state}")
        if params.theme:
            query_parts.append(f"theme={params.theme}")
        
        query = "^".join(query_parts) if query_parts else None
        
        params_dict = {
            "sysparm_limit": params.limit,
            "sysparm_offset": params.offset,
        }
        
        if query:
            params_dict["sysparm_query"] = query
        
        return await client.send_request("GET", "/api/now/table/rm_epic", params=params_dict)