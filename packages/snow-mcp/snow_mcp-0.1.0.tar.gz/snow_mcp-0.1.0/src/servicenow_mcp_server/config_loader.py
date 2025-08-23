import os
import json
from dotenv import load_dotenv

def load_config():
    """
    Loads ServiceNow configuration with the following priority:
    1. Environment variables (e.g., SERVICENOW_INSTANCE).
    2. A .env file in the current working directory.
    3. A JSON file specified by the SERVICENOW_CONFIG_JSON env var.
    """
    # Load .env file contents into environment variables
    load_dotenv()

    # Priority 1: Check for explicit environment variables
    env_vars = ["SERVICENOW_INSTANCE", "SERVICENOW_USERNAME", "SERVICENOW_PASSWORD"]
    if all(os.getenv(v) for v in env_vars):
        return {k.replace("SERVICENOW_", "").lower(): os.getenv(k) for k in env_vars}

    # Priority 2: Check for JSON file path
    json_path = os.getenv("SERVICENOW_CONFIG_JSON")
    if json_path and os.path.exists(json_path):
        with open(json_path, "r") as f:
            return json.load(f)

    # If neither is found, raise an error
    raise RuntimeError(
        "ServiceNow config not found. Please provide either environment variables "
        "(SERVICENOW_INSTANCE, etc.), a .env file, or a SERVICENOW_CONFIG_JSON path."
    )