# src/servicenow_mcp_server/agile_management/scrum_tools.py

"""
This module defines tools for interacting with Scrum Tasks in ServiceNow's
Agile Development application.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from fastmcp import FastMCP
from servicenow_mcp_server.utils import ServiceNowClient

# Local MCP instance for decorating tools
mcp = FastMCP()

def register_tools(mcp: FastMCP):
    """Adds all tools defined in this file to the main server's MCP instance."""
    mcp.add_tool(create_scrum_task)
    mcp.add_tool(update_scrum_task)
    mcp.add_tool(list_scrum_tasks)

# ==============================================================================
#  Pydantic Models
# ==============================================================================

class BaseToolParams(BaseModel):
    instance_url: str = Field(..., description="The full URL of the ServiceNow instance.")
    username: str = Field(..., description="The username for authentication.")
    password: str = Field(..., description="The password for authentication.", sensitive=True)

class CreateScrumTaskParams(BaseToolParams):
    short_description: str = Field(..., description="A brief summary of the scrum task.")
    story_sys_id: str = Field(..., description="The sys_id of the parent story this task belongs to.")
    description: Optional[str] = Field(None, description="A detailed description of the task.")
    assignment_group: Optional[str] = Field(None, description="The sys_id of the group to assign the task to.")
    assigned_to: Optional[str] = Field(None, description="The sys_id of the user to assign the task to.")
    remaining_hours: Optional[float] = Field(None, description="Estimated remaining hours to complete the task.")

class UpdateScrumTaskParams(BaseToolParams):
    sys_id: str = Field(..., description="The sys_id of the scrum task to update.")
    short_description: Optional[str] = Field(None, description="A brief summary of the scrum task.")
    description: Optional[str] = Field(None, description="A detailed description of the task.")
    assignment_group: Optional[str] = Field(None, description="The sys_id of the group to assign the task to.")
    assigned_to: Optional[str] = Field(None, description="The sys_id of the user to assign the task to.")
    remaining_hours: Optional[float] = Field(None, description="Estimated remaining hours to complete the task.")
    state: Optional[str] = Field(None, description="Task state (e.g., -3: Draft, -2: Ready, -1: Blocked, 0: Open, 1: Work in Progress, 2: Closed Complete, 3: Closed Incomplete, 4: Closed Skipped).")

class ListScrumTasksParams(BaseToolParams):
    story_sys_id: Optional[str] = Field(None, description="Return only tasks that belong to this story.")
    assigned_to: Optional[str] = Field(None, description="Return only tasks assigned to this user.")
    assignment_group: Optional[str] = Field(None, description="Return only tasks assigned to this group.")
    state: Optional[str] = Field(None, description="Return only tasks in this state.")
    limit: int = Field(10, description="Maximum number of records to return (max 100).")
    offset: int = Field(0, description="Number of records to skip for pagination.")

# ==============================================================================
#  Tool Functions
# ==============================================================================

@mcp.tool()
async def create_scrum_task(params: CreateScrumTaskParams) -> Dict[str, Any]:
    """
    Creates a new scrum task and associates it with a parent story.
    """
    async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
        # The table for scrum tasks is 'rm_scrum_task'.
        payload = {
            "short_description": params.short_description,
            "story": params.story_sys_id, # The reference field to the story table is 'story'
            "description": params.description,
            "assignment_group": params.assignment_group,
            "assigned_to": params.assigned_to,
            "remaining_hours": params.remaining_hours
        }
        
        # Filter out any None values before sending
        final_payload = {k: v for k, v in payload.items() if v is not None}
        
        return await client.send_request("POST", "/api/now/table/rm_scrum_task", data=final_payload)

@mcp.tool()
async def update_scrum_task(params: UpdateScrumTaskParams) -> Dict[str, Any]:
    """
    Updates an existing scrum task in ServiceNow.
    """
    async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
        payload = {
            "short_description": params.short_description,
            "description": params.description,
            "assignment_group": params.assignment_group,
            "assigned_to": params.assigned_to,
            "remaining_hours": params.remaining_hours,
            "state": params.state
        }
        final_payload = {k: v for k, v in payload.items() if v is not None}

        return await client.send_request(
            "PATCH",
            f"/api/now/table/rm_scrum_task/{params.sys_id}",
            data=final_payload
        )

@mcp.tool()
async def list_scrum_tasks(params: ListScrumTasksParams) -> Dict[str, Any]:
    """
    Lists scrum tasks from ServiceNow with optional filters.
    """
    async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
        query_parts = []
        if params.story_sys_id:
            query_parts.append(f"story={params.story_sys_id}")
        if params.assigned_to:
            query_parts.append(f"assigned_to={params.assigned_to}")
        if params.assignment_group:
            query_parts.append(f"assignment_group={params.assignment_group}")
        if params.state:
            query_parts.append(f"state={params.state}")

        query = "^".join(query_parts)
        params_dict = {
            "sysparm_limit": min(max(params.limit, 1), 100),
            "sysparm_offset": max(params.offset, 0)
        }
        if query:
            params_dict["sysparm_query"] = query

        return await client.send_request(
            "GET",
            "/api/now/table/rm_scrum_task",
            params=params_dict
        )


