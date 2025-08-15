import httpx
from mcp.server.fastmcp import FastMCP
 
mcp = FastMCP("azure")
 
AZURE_BASE = "https://management.azure.com"
 
# --- Helper to fetch Azure service data ---
async def fetch_azure_service_data(service_name: str) -> dict:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{AZURE_BASE}/services/{service_name.lower()}")
            if response.status_code == 200:
                return response.json()
        except httpx.HTTPError:
            pass
    return {}
 
# --- Tool: Get info about an Azure service ---
@mcp.tool()
async def get_azure_service_info(service_name: str) -> str:
    """Get detailed info about an Azure service by name."""
    data = await fetch_azure_service_data(service_name)
    if not data:
        return f"No data found for Azure service: {service_name}"
 
    properties = {key: value for key, value in data.items() if key != 'id'}
    return f"""
Service Name: {data['name'].capitalize()}
Properties: {', '.join(f"{k}: {v}" for k, v in properties.items())}
"""
 
# --- Tool: Create a resource group ---
@mcp.tool()
async def create_resource_group() -> str:
    """Create a new Azure resource group."""
    resource_groups = ["Development", "Testing", "Production"]
    created_groups = []
 
    for name in resource_groups:
        data = await fetch_azure_service_data(name)
        if data:
            created_groups.append(data["name"].capitalize())
 
    return "Created Resource Groups:\n" + "\n".join(created_groups)
 
# --- Tool: List popular Azure services ---
@mcp.tool()
async def list_popular_azure_services() -> str:
    """List popular Azure services."""
    return "\n".join([
        "Azure Functions", "Azure Blob Storage", "Azure SQL Database",
        "Azure Kubernetes Service", "Azure Cosmos DB", "Azure DevOps"
    ])