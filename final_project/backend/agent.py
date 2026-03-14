import os
from pydantic_ai import Agent, RunContext
from dotenv import load_dotenv

load_dotenv()

# Read the preferred model from .env (fallback to gemini)
AI_MODEL = os.getenv("AI_MODEL", "gemini-2.0-flash")

# Define the Agent dynamically based on the .env variable
agent = Agent(
    AI_MODEL,
    system_prompt=(
        "You are a specialized Biodiversity Agent. Your goal is to help users understand "
        "and protect the environment.\n"
        "You have access to tools that can analyze satellite data, wildlife camera traps, "
        "and ocean sensors to detect illegal activities such as deforestation or illegal trawling.\n"
        "When such activities are detected, you must alert the authorities using the provided tool.\n"
        "Always be helpful, precise, and advocate for nature conservation."
    ),
)


@agent.tool
async def analyze_satellite_imagery(ctx: RunContext[None], coordinates: str) -> str:
    """
    Analyzes satellite imagery for a given set of coordinates to detect deforestation or other illegal activities.
    
    Args:
        coordinates: The lat/lon coordinates to check (e.g., "Lat: -3.4, Lon: -62.1" or "Amazon").
    """
    print(f"[TOOL RUN] Analyzing satellite imagery at {coordinates}...")
    # Mocking real-time detection logic:
    if "Amazon" in coordinates or "-62" in coordinates or "Brazil" in coordinates:
        return "ALERT: Satellite imagery indicates a 15% increase in illegal logging roads compared to last month."
    return "Satellite imagery shows stable forest cover. No anomalies detected."


@agent.tool
async def analyze_ocean_sensors(ctx: RunContext[None], marine_region: str) -> str:
    """
    Analyzes data from ocean sensors (acoustic, sonar) in a given marine region to detect illegal fishing/trawling.
    
    Args:
        marine_region: The name or coordinates of the marine region (e.g., "Galapagos Marine Reserve").
    """
    print(f"[TOOL RUN] Analyzing ocean sensors in {marine_region}...")
    if "Galapagos" in marine_region or "Pacific" in marine_region:
        return "ALERT: Acoustic sensors detected signature sounds of bottom-trawling nets in a protected area."
    return "Ocean sensor data is normal. Marine life sounds are healthy."


@agent.tool
async def analyze_wildlife_cameras(ctx: RunContext[None], park_name: str) -> str:
    """
    Analyzes photographs from wildlife camera traps in a given national park.
    
    Args:
        park_name: The name of the national park to analyze.
    """
    print(f"[TOOL RUN] Analyzing wildlife cameras in {park_name}...")
    if "Serengeti" in park_name or "Kruger" in park_name:
        return "ALERT: Camera traps captured images of unauthorized individuals carrying hunting rifles at night."
    return "Camera traps mainly show normal wildlife movement (e.g., jaguars, tapirs, monkeys)."


@agent.tool
async def alert_authorities(ctx: RunContext[None], location: str, violation_type: str, severity: str) -> str:
    """
    Alerts the local environmental authorities about an ongoing illegal activity.
    
    Args:
        location: The location of the violation.
        violation_type: The type of violation (e.g., "Deforestation", "Illegal Trawling", "Poaching").
        severity: High, Medium, or Low.
    """
    print(f"[TOOL RUN] ALERTING AUTHORITIES! Location: {location}, Violation: {violation_type}, Severity: {severity}")
    return f"Successfully dispatched an alert to environmental law enforcement for {violation_type} at {location} (Severity: {severity})."
