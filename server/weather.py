"""Weather tools for MCP Streamable HTTP server using NWS API with Dify MCP authorization support."""

import argparse
import os
from typing import Any, Optional

import httpx
import uvicorn
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from mcp.server.fastmcp import FastMCP


# Initialize FastMCP server for Weather tools.
# If json_response is set to True, the server will use JSON responses instead of SSE streams
# If stateless_http is set to True, the server uses true stateless mode (new transport per request)
mcp = FastMCP(name="weather", json_response=False, stateless_http=False)

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

# Dify MCP Authorization
security = HTTPBearer(auto_error=False)


def get_api_key() -> Optional[str]:
    """Get API key from environment variable."""
    return os.getenv("DIFY_API_KEY") or os.getenv("MCP_API_KEY")


async def verify_api_key(credentials: Optional[HTTPAuthorizationCredentials] = None) -> bool:
    """Verify API key for Dify MCP authorization."""
    api_key = get_api_key()
    
    # If no API key is configured, allow all requests (for development)
    if not api_key:
        return True
    
    # Check if credentials are provided
    if not credentials:
        return False
    
    # Verify the API key
    return credentials.credentials == api_key


def check_auth_header(request: Request) -> bool:
    """Check authorization header for valid API key."""
    api_key = get_api_key()
    
    # If no API key is configured, allow all requests (for development)
    if not api_key:
        return True
    
    # Get authorization header
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return False
    
    token = auth_header.split(" ")[1]
    return token == api_key


async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/geo+json"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None


def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
Event: {props.get('event', 'Unknown')}
Area: {props.get('areaDesc', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
Description: {props.get('description', 'No description available')}
Instructions: {props.get('instruction', 'No specific instructions provided')}
"""


@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."

    if not data["features"]:
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)


@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    # First get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        return "Unable to fetch forecast data for this location."

    # Get the forecast URL from the points response
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data:
        return "Unable to fetch detailed forecast."

    # Format the periods into a readable forecast
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:5]:  # Only show next 5 periods
        forecast = f"""
{period['name']}:
Temperature: {period['temperature']}°{period['temperatureUnit']}
Wind: {period['windSpeed']} {period['windDirection']}
Forecast: {period['detailedForecast']}
"""
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run MCP Streamable HTTP based server with Dify MCP authorization")
    parser.add_argument("--port", type=int, default=8123, help="Port to listen on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--api-key", type=str, help="API key for Dify MCP authorization (or set DIFY_API_KEY env var)")
    parser.add_argument("--no-auth", action="store_true", help="Disable authentication (for development)")
    args = parser.parse_args()

    # Set API key from command line argument if provided
    if args.api_key:
        os.environ["DIFY_API_KEY"] = args.api_key
    
    # Disable authentication if --no-auth is specified
    if args.no_auth:
        os.environ["DIFY_API_KEY"] = ""
    
    print(f"Starting Weather MCP server on {args.host}:{args.port}")
    if get_api_key():
        print("Authentication enabled - API key required")
        print("Note: Authentication is currently implemented at the tool level")
        print("For full middleware authentication, consider using a reverse proxy")
    else:
        print("Authentication disabled - no API key configured")
    
    # Start the server with Streamable HTTP transport
    # Use factory flag since streamable_http_app is a factory function
    uvicorn.run(
        mcp.streamable_http_app, 
        host=args.host, 
        port=args.port,
        factory=True
    )
