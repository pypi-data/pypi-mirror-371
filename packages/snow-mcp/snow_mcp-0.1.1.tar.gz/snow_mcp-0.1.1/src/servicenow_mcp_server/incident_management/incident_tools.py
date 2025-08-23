# src/servicenow_mcp_server/incident_management/incident_tools.py

"""
This module defines and registers tools for ServiceNow Incident Management.
Each tool expects all required parameters, including ServiceNow credentials,
to be passed directly in the 'params' object of the tool call.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from fastmcp import FastMCP
from servicenow_mcp_server.utils import ServiceNowClient

mcp = FastMCP(name="ServiceNow Incident Management Tools")
# ==============================================================================
#  Tool Registration Function
# ==============================================================================

def register_tools(mcp: FastMCP):
    """
    Registers all incident management tools with the main MCP server instance.
    """
    
    mcp.add_tool(create_incident)
    mcp.add_tool(get_incident)
    mcp.add_tool(list_incidents)
    mcp.add_tool(update_incident)
    mcp.add_tool(add_comment_to_incident)
    mcp.add_tool(resolve_incident)
    mcp.add_tool(list_recent_incidents)
    mcp.add_tool(get_incident_by_number)
    mcp.add_tool(add_work_notes_to_incident)


# ==============================================================================
#  Pydantic Models for Input Schemas
# ==============================================================================

class BaseToolParams(BaseModel):
    """A base model containing the required ServiceNow credentials for any tool call."""
    instance_url: str = Field(..., description="The full URL of the ServiceNow instance (e.g., https://my-instance.service-now.com).")
    username: str = Field(..., description="The username for authentication.")
    password: str = Field(..., description="The password for authentication.", sensitive=True)

# Each tool-specific parameter model inherits the base credentials
class CreateIncidentParams(BaseToolParams):
    short_description: str = Field(..., description="A brief, one-line summary of the incident.")
    description: Optional[str] = Field(None, description="A detailed description of the incident.")
    caller_id: Optional[str] = Field(None, description="The sys_id of the user reporting the incident.")
    urgency: str = Field("3", description="Urgency of the incident (1-High, 2-Medium, 3-Low).")
    impact: str = Field("3", description="Impact of the incident (1-High, 2-Medium, 3-Low).")
    assignment_group: Optional[str] = Field(None, description="The sys_id of the group to assign the incident to.")
    
class GetIncidentParams(BaseToolParams):
    sys_id: str = Field(..., description="The unique system ID (sys_id) of the incident to retrieve.")

class ListIncidentsParams(BaseToolParams):
    query: Optional[str] = Field(None, description="An encoded ServiceNow query string (e.g., 'active=true^priority=1').")
    limit: int = Field(10, description="The maximum number of incidents to return.")
    offset: int = Field(0, description="The starting record number for pagination.")
    fields: Optional[List[str]] = Field(None, description="A list of specific fields to return (e.g., ['number', 'short_description']).")

class UpdateIncidentParams(BaseToolParams):
    sys_id: str = Field(..., description="The unique system ID (sys_id) of the incident to update.")
    work_notes: Optional[str] = Field(None, description="Internal work notes to add to the incident.")
    state: Optional[str] = Field(None, description="The new state of the incident (e.g., '2' for In Progress).")
    priority: Optional[str] = Field(None, description="The new priority of the incident (e.g., '1' for Critical).")
    assignment_group: Optional[str] = Field(None, description="The sys_id of the group to re-assign the incident to.")
    
class CommentParams(BaseToolParams):
    sys_id: str = Field(..., description="The sys_id of the incident to which the comment will be added.")
    comment: str = Field(..., description="The customer-visible comment to add.")

class ResolveParams(BaseToolParams):
    sys_id: str = Field(..., description="The sys_id of the incident to resolve.")
    close_notes: str = Field(..., description="Mandatory notes describing the resolution.")
    close_code: str = Field("Solved (Permanently)", description="The code indicating how the incident was resolved.")

class ListRecentIncidentsParams(BaseToolParams):
    limit: int = Field(10, description="The maximum number of recent incidents to return.")

class GetIncidentByNumberParams(BaseToolParams):
    number: str = Field(..., description="The human-readable incident number (e.g., 'INC0010107').")

class WorkNotesParams(BaseToolParams):
    sys_id: str = Field(..., description="The sys_id of the incident to which the work notes will be added.")
    notes: str = Field(..., description="The internal-only work notes to add.")

class UpdateIncidentParams(BaseToolParams):
    sys_id: str = Field(..., description="The unique system ID (sys_id) of the incident to update.")
    short_description: Optional[str] = Field(None, description="A new one-line summary for the incident.")
    description: Optional[str] = Field(None, description="A new detailed description for the incident.")
    state: Optional[str] = Field(None, description="The new state for the incident (e.g., '2' for In Progress, '6' for Resolved).")
    priority: Optional[str] = Field(None, description="The new priority for the incident (e.g., '1' for Critical).")
    urgency: Optional[str] = Field(None, description="The new urgency for the incident (1-High, 2-Medium, 3-Low).")
    impact: Optional[str] = Field(None, description="The new impact for the incident (1-High, 2-Medium, 3-Low).")
    assignment_group: Optional[str] = Field(None, description="The sys_id of the group to re-assign the incident to.")
    assigned_to: Optional[str] = Field(None, description="The sys_id of the user to assign the incident to.")

# ==============================================================================
#  Tool Functions
# ==============================================================================

@mcp.tool()
async def create_incident(params: CreateIncidentParams) -> Dict[str, Any]:
    """Creates a new incident. Credentials must be provided in the params object."""
    async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
        incident_data = params.model_dump(exclude={"instance_url", "username", "password"}, exclude_unset=True)
        return await client.send_request("POST", "/api/now/table/incident", data=incident_data)

@mcp.tool()
async def get_incident(params: GetIncidentParams) -> Dict[str, Any]:
    """Retrieves the full details of a single incident by its unique sys_id."""
    async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
        return await client.send_request("GET", f"/api/now/table/incident/{params.sys_id}")

@mcp.tool()
async def list_incidents(params: ListIncidentsParams) -> Dict[str, Any]:
    """Lists incidents based on a query, with support for pagination and field selection."""
    async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
        query_params = {
            "sysparm_limit": params.limit,
            "sysparm_offset": params.offset,
        }
        if params.query:
            query_params["sysparm_query"] = params.query
        if params.fields:
            query_params["sysparm_fields"] = ",".join(params.fields)
        return await client.send_request("GET", "/api/now/table/incident", params=query_params)

@mcp.tool()
async def update_incident(params: UpdateIncidentParams) -> Dict[str, Any]:
    """Updates an existing incident with new information like work notes, state, or priority."""
    async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
        update_data = params.model_dump(exclude={"sys_id", "instance_url", "username", "password"}, exclude_unset=True)
        if not update_data:
            return {"error": "No update data provided."}
        return await client.send_request("PATCH", f"/api/now/table/incident/{params.sys_id}", data=update_data)


@mcp.tool()
async def add_comment_to_incident(params: CommentParams) -> Dict[str, Any]:
    """
    Adds a customer-visible comment (updates the 'comments' field) to an existing incident.
    """
    async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
        # The 'comments' field is the specific target for customer-visible notes.
        update_data = {"comments": params.comment}
        
        endpoint = f"/api/now/table/incident/{params.sys_id}"
        
        return await client.send_request("PATCH", endpoint, data=update_data)

@mcp.tool()
async def resolve_incident(params: ResolveParams) -> Dict[str, Any]:
    """Resolves an incident by setting its state to 'Resolved' and adding resolution notes."""
    async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
        resolve_data = {
            "state": "6",
            "incident_state": "6",
            "close_notes": params.close_notes,
            "close_code": params.close_code,
        }
        return await client.send_request("PATCH", f"/api/now/table/incident/{params.sys_id}", data=resolve_data)
    

@mcp.tool()
async def list_recent_incidents(params: ListRecentIncidentsParams) -> Dict[str, Any]:
    """
    Fetches a list of the most recently created incidents.
    """
    async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
        query_params = {
            # This query orders results by the 'sys_created_on' field in descending order
            "sysparm_query": "ORDERBYDESCsys_created_on",
            "sysparm_limit": params.limit,
            "sysparm_fields": "number,short_description,state,priority,sys_created_on"
        }
        return await client.send_request("GET", "/api/now/table/incident", params=query_params)
    
@mcp.tool()
async def get_incident_by_number(params: GetIncidentByNumberParams) -> Dict[str, Any]:
    """
    Finds and retrieves a single incident by its number (e.g., 'INC0010107').
    """
    async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
        query_params = {
            "sysparm_query": f"number={params.number}",
            "sysparm_limit": 1
        }
        response = await client.send_request("GET", "/api/now/table/incident", params=query_params)
        
        # The API returns a list in the 'result' field. Check if it's empty.
        if response and response.get('result'):
            # If found, return the first (and only) item in the list.
            return {"result": response['result'][0]}
        
        # If the list is empty or doesn't exist, the incident was not found.
        return {"error": "Not Found", "message": f"Incident with number '{params.number}' was not found."}

@mcp.tool()
async def update_incident(params: UpdateIncidentParams) -> Dict[str, Any]:
    """
    Updates one or more fields on an existing incident record.
    Only the fields provided in the call will be changed.
    """
    async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
        # Pydantic's model_dump is perfect for this.
        # It creates a dictionary of the model's data.
        # `exclude_unset=True` means it will only include fields that were
        # explicitly provided in the API call, ignoring all the 'None' values.
        # We also exclude the credentials and sys_id, as they aren't part of the update payload.
        update_data = params.model_dump(
            exclude={"sys_id", "instance_url", "username", "password"},
            exclude_unset=True
        )

        if not update_data:
            return {"error": "No update data provided.", "message": "You must provide at least one field to update besides the sys_id."}

        # The sys_id is used to build the endpoint URL
        endpoint = f"/api/now/table/incident/{params.sys_id}"
        
        # Use the HTTP PATCH method for partial updates.
        return await client.send_request("PATCH", endpoint, data=update_data)
    
@mcp.tool()
async def add_work_notes_to_incident(params: WorkNotesParams) -> Dict[str, Any]:
    """
    Adds internal work notes (updates the 'work_notes' field) to an existing incident.
    """
    async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
        # The 'work_notes' field is the specific target for internal notes.
        update_data = {"work_notes": params.notes}
        
        endpoint = f"/api/now/table/incident/{params.sys_id}"
        
        return await client.send_request("PATCH", endpoint, data=update_data)