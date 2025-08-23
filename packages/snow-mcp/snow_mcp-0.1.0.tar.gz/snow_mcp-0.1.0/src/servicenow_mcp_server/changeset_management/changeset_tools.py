# src/servicenow_mcp_server/changeset_management/changeset_tools.py

"""
This module defines tools for interacting with ServiceNow Update Sets (Changesets).
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from fastmcp import FastMCP
from servicenow_mcp_server.utils import ServiceNowClient

# Local MCP instance for decorating tools
mcp = FastMCP()

def register_tools(mcp: FastMCP):
    """Adds all tools defined in this file to the main server's MCP instance."""
    mcp.add_tool(list_changesets)
    mcp.add_tool(get_changeset_details)
    mcp.add_tool(create_changeset)
    mcp.add_tool(update_changeset)
    mcp.add_tool(commit_changeset)
    mcp.add_tool(publish_changeset)
    mcp.add_tool(add_file_to_changeset)

# ==============================================================================
#  Pydantic Models
# ==============================================================================

class BaseToolParams(BaseModel):
    instance_url: str = Field(..., description="The full URL of the ServiceNow instance.")
    username: str = Field(..., description="The username for authentication.")
    password: str = Field(..., description="The password for authentication.", sensitive=True)

class ListChangesetsParams(BaseToolParams):
    state_filter: Optional[str] = Field("in progress", description="Filter by state (e.g., 'in progress', 'complete').")
    name_filter: Optional[str] = Field(None, description="A search term to filter changesets by name.")
    created_by_filter: Optional[str] = Field(None, description="Filter by the username of the creator.")
    limit: int = Field(20, description="The maximum number of records to return.")

class GetChangesetDetailsParams(BaseToolParams):
    sys_id: str = Field(..., description="The sys_id of the changeset to retrieve.")

class CreateChangesetParams(BaseToolParams):
    name: str = Field(..., description="The name of the new changeset.")
    description: Optional[str] = Field(None, description="Description of the changeset.")

class UpdateChangesetParams(BaseToolParams):
    sys_id: str = Field(..., description="The sys_id of the changeset to update.")
    name: Optional[str] = Field(None, description="New name for the changeset.")
    description: Optional[str] = Field(None, description="Updated description.")

class CommitChangesetParams(BaseToolParams):
    sys_id: str = Field(..., description="The sys_id of the changeset to commit.")

class PublishChangesetParams(BaseToolParams):
    sys_id: str = Field(..., description="The sys_id of the changeset to publish.")

class AddFileToChangesetParams(BaseToolParams):
    changeset_sys_id: str = Field(..., description="The sys_id of the changeset.")
    file_type: str = Field(..., description="Type of configuration file (e.g., 'sys_script', 'sys_script_include').")
    file_sys_id: str = Field(..., description="The sys_id of the record to add to the changeset.")

# ==============================================================================
#  Tool Functions
# ==============================================================================

@mcp.tool()
async def list_changesets(params: ListChangesetsParams) -> Dict[str, Any]:
    """
    Lists local Update Sets (Changesets), with options to filter.
    """
    async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
        # The table for Update Sets is 'sys_update_set'.
        query_parts = []

        if params.state_filter:
            query_parts.append(f"state={params.state_filter}")
        if params.name_filter:
            query_parts.append(f"nameLIKE{params.name_filter}")
        if params.created_by_filter:
            query_parts.append(f"sys_created_by={params.created_by_filter}")

        final_query = "^".join(query_parts)

        query_params = {
            "sysparm_query": final_query,
            "sysparm_limit": params.limit,
            "sysparm_fields": "name,state,sys_id,sys_created_by,description"
        }
        
        return await client.send_request("GET", "/api/now/table/sys_update_set", params=query_params)
    


@mcp.tool()
async def get_changeset_details(params: GetChangesetDetailsParams) -> Dict[str, Any]:
    """
    Retrieve full details for a single changeset.
    """
    async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
        return await client.send_request(
            "GET",
            f"/api/now/table/sys_update_set/{params.sys_id}"
        )

@mcp.tool()
async def create_changeset(params: CreateChangesetParams) -> Dict[str, Any]:
    """
    Create a new local Update Set (changeset).
    """
    async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
        payload = params.model_dump(
            exclude={"instance_url", "username", "password"},
            exclude_unset=True
        )
        payload.setdefault("state", "in progress")
        return await client.send_request(
            "POST",
            "/api/now/table/sys_update_set",
            data=payload
        )

@mcp.tool()
async def update_changeset(params: UpdateChangesetParams) -> Dict[str, Any]:
    """
    Update an existing changeset (name or description).
    """
    async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
        payload = params.model_dump(
            exclude={"instance_url", "username", "password", "sys_id"},
            exclude_unset=True
        )
        return await client.send_request(
            "PATCH",
            f"/api/now/table/sys_update_set/{params.sys_id}",
            data=payload
        )

@mcp.tool()
async def commit_changeset(params: CommitChangesetParams) -> Dict[str, Any]:
    """
    Mark a changeset as complete (state = 'complete').
    """
    async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
        payload = {"state": "complete"}
        return await client.send_request(
            "PATCH",
            f"/api/now/table/sys_update_set/{params.sys_id}",
            data=payload
        )

@mcp.tool()
async def publish_changeset(params: PublishChangesetParams) -> Dict[str, Any]:
    """
    Publish a completed changeset so it can be retrieved from the remote instance.
    """
    async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
        return await client.send_request(
            "POST",
            f"/api/now/publish/update_set/{params.sys_id}"
        )

@mcp.tool()
async def add_file_to_changeset(params: AddFileToChangesetParams) -> Dict[str, Any]:
    """
    Add (track) a configuration record inside the specified changeset.
    """
    async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
        payload = {
            "update_set": params.changeset_sys_id,
            "type": params.file_type,
            "target_sys_id": params.file_sys_id
        }
        return await client.send_request(
            "POST",
            "/api/now/table/sys_update_xml",
            data=payload
        )
