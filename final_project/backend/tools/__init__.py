"""
Módulo de herramientas para el agente de biodiversidad.
Exporta las herramientas refactorizadas y registradas.
"""
from .biodiversity_tools import (
    analyze_deforestation,
    detect_illegal_fishing,
    monitor_wildlife,
    get_environmental_data,
    generate_conservation_report,
    check_alert_status,
    search_biodiversity_database
)

# Registro centralizado de herramientas para CopilotKit/LangChain
TOOLS_REGISTRY = [
    analyze_deforestation,
    detect_illegal_fishing, 
    monitor_wildlife,
    get_environmental_data,
    generate_conservation_report,
    check_alert_status,
    search_biodiversity_database
]

__all__ = [
    "TOOLS_REGISTRY",
    "analyze_deforestation",
    "detect_illegal_fishing",
    "monitor_wildlife", 
    "get_environmental_data",
    "generate_conservation_report",
    "check_alert_status",
    "search_biodiversity_database"
]