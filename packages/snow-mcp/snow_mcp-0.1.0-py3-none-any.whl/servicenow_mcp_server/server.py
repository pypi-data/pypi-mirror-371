import logging
import asyncio
from fastmcp import FastMCP

from servicenow_mcp_server.incident_management import incident_tools
from servicenow_mcp_server.table_management import table_tools
from servicenow_mcp_server.user_management import user_tools 
from servicenow_mcp_server.service_catalog import catalog_tools
from servicenow_mcp_server.change_management import change_tools
from servicenow_mcp_server.agile_management import story_tools
from servicenow_mcp_server.agile_management import epic_tools
from servicenow_mcp_server.agile_management import scrum_tools
from servicenow_mcp_server.project_management import project_tools
from servicenow_mcp_server.workflow_management import workflow_tools  
from servicenow_mcp_server.script_include_management import script_include_tools
from servicenow_mcp_server.changeset_management import changeset_tools 
from servicenow_mcp_server.kb_management import kb_tools   
from servicenow_mcp_server.ui_policy_management import ui_policy_tools  
from servicenow_mcp_server.request_management import request_tools
#from servicenow_mcp_server.natural_language import nl_tools
from servicenow_mcp_server.analytics import analytics_tools


logging.basicConfig(level=logging.INFO, format="[SERVER] %(message)s")

def main():
    logging.info("Starting ServiceNow MCP Server (Client-Side Credentials Mode)...")

    mcp = FastMCP(name="ServiceNow MCP Server")
    
    # The server no longer manages a central client or state.
    # mcp.state["servicenow_client"] is NOT set.

    logging.info("Registering Incident Management tools...")
    incident_tools.register_tools(mcp)

    logging.info("Registering Table Management tools...")
    table_tools.register_tools(mcp)
    
    logging.info("Registering User Management tools...")
    user_tools.register_tools(mcp)

    logging.info("Registering Service Catalog tools...")
    catalog_tools.register_tools(mcp)

    logging.info("Registering Agile Management tools...")
    story_tools.register_tools(mcp)

    logging.info("Registering Change Management tools...")
    change_tools.register_tools(mcp)

    logging.info("Registering Epic Management tools...")
    epic_tools.register_tools(mcp)

    logging.info("Registering Scrum Task tools...")
    scrum_tools.register_tools(mcp)

    logging.info("Registering Project Management tools...")
    project_tools.register_tools(mcp)

    logging.info("Registering Workflow Management tools...")
    workflow_tools.register_tools(mcp)

    logging.info("Registering Script Include Management tools...")
    script_include_tools.register_tools(mcp)

    logging.info("Registering Changeset Management tools...")
    changeset_tools.register_tools(mcp)

    logging.info("Registering Knowledge Base Management tools...")
    kb_tools.register_tools(mcp)

    logging.info("Registering UI Policy Management tools...")
    ui_policy_tools.register_tools(mcp)

    logging.info("Registering Request Management tools...")
    request_tools.register_tools(mcp)

    logging.info("Registering Analytics tools...")
    analytics_tools.register_tools(mcp)

    #logging.info("Registering Natural Language tools...")
    #nl_tools.register_tools(mcp)
    
    logging.info("All tools registered. Server is ready to accept requests.")
    
    # The `finally` block is removed as there's no central client to close.
    mcp.run(transport="stdio")
    
    logging.info("Server stopped.")

if __name__ == "__main__":
    # The main function is not async anymore since we removed the async client shutdown
    main()  