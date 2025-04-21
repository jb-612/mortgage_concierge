"""
Generate RestApiTool instances from the mortgage calculator OpenAPI spec.
"""
import os
from pathlib import Path

import yaml
from google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset import OpenAPIToolset


def load_loan_calculator_api_tools():
    """
    Load the OpenAPI spec for the loan calculator and return generated RestApiTool tools.
    Requires a spec file at mortgage_concierge/openapi/loan_calculator.yaml.
    """
    # Resolve path to the spec file within the mortgage_concierge package
    # __file__ is .../mortgage_concierge/tools/openapi_tools.py; parents[1] is the mortgage_concierge package root
    spec_file = Path(__file__).resolve().parents[1] / "openapi" / "loan_calculator.yaml"
    if not spec_file.exists():
        raise FileNotFoundError(f"OpenAPI spec not found at {spec_file}. Ensure the file is under mortgage_concierge/openapi/")
    # Load spec (YAML or JSON)
    with open(spec_file, 'r') as f:
        spec_dict = yaml.safe_load(f)

    # Optionally override server URL via env var
    base_url = os.getenv("LOAN_CALCULATOR_API_BASE_URL")
    if base_url:
        # update servers[0].url if present
        if "servers" in spec_dict and isinstance(spec_dict["servers"], list):
            spec_dict["servers"][0]["url"] = base_url
        else:
            spec_dict["servers"] = [{"url": base_url}]

    # Instantiate OpenAPIToolset
    toolset = OpenAPIToolset(spec_dict=spec_dict)
    # Return list of RestApiTool instances
    return toolset.get_tools()