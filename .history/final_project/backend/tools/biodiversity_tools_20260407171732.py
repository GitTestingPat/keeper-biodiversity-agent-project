"""
Herramientas para el agente de biodiversidad.
Compatible con langchain>=0.3.0 y copilotkit>=0.1.20
"""
import asyncio
from typing import Optional
from langchain_core.tools import tool

# Imports de servicios
from services.satellite_service import satellite_service
from services.ocean_service import ocean_service
from services.wildlife_service import wildlife_service
from services.alert_service import alert_service, AlertType, AlertSeverity
from config.settings import settings


@tool
async def analyze_deforestation(
    location: str,
    coordinates: Optional[str] = None,
    days_back: int = 30
) -> dict:
    """
    Analiza cambios en cobertura forestal usando datos satelitales.

    Args:
        location: Nombre de la ubicación (ej: "Amazonas", "Borneo",
        "Parque Nacional Yasuní")
        coordinates: Coordenadas opcionales en formato "Lat: X, Lon: Y"
        days_back: Días hacia atrás para el análisis (default: 30)

    Returns:
        Dict con análisis de deforestación, alertas y recomendaciones
    """
    try:
        # Si hay coordenadas, usarlas directamente
        if coordinates and "Lat:" in coordinates and "Lon:" in coordinates:
            parts = coordinates.replace(",", "").split()
            lat = float([p for p in parts if p.replace("-", "").replace(".", "").isdigit()][0])
            lon = float([p for p in parts if p.replace("-", "").replace(".", "").isdigit()][1])
            result = await satellite_service.get_deforestation_alert(lat, lon, days_back)
        else:
            # Usar nombre de región
            result = await satellite_service.analyze_region(location)

        # Si se detecta alerta crítica, crear entrada en alert_service
        if result.get("alerts"):
            for alert in result["alerts"]:
                if alert.get("severity") == "HIGH":
                    alert_obj = alert_service.create_alert(
                        alert_type=AlertType.DEFORESTATION_DETECTED,
                        severity=AlertSeverity.HIGH,
                        location={"name": location, "coordinates": result.get("location")},
                        description=alert.get("description", "Deforestación detectada"),
                        metadata={"source": "satellite_analysis", "raw_data": result}
                    )
                    # Enviar solo a log en modo demostración
                    await alert_service.send_alert(alert_obj, channels=['log'])

        return {
            "success": True,
            "data": result,
            "message": f"Análisis completado para {location}"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error analizando deforestación."
            "Verifica los parámetros."
        }


@tool
async def detect_illegal_fishing(
    marine_region: str,
    radius_km: float = 50.0
) -> dict:
    """
    Detecta actividad de pesca ilegal mediante análisis de sensores oceánicos.

    Args:
        marine_region: Nombre de la región marina (ej: "Galápagos",
        "Great Barrier Reef")
        radius_km: Radio de análisis en kilómetros (default: 50)

    Returns:
        Dict con detección de actividad sospechosa y nivel de riesgo
    """
    try:
        result = await ocean_service.detect_illegal_trawling(
            marine_region, radius_km
            )

        # Generar alerta si hay riesgo alto en área protegida
        if result.get("assessment", {}).get("risk_level") == "HIGH":
            alert_obj = alert_service.create_alert(
                alert_type=AlertType.ILLEGAL_TRAWLING,
                severity=AlertSeverity.CRITICAL,
                location={"name": result["location"]["region"]},
                description="Actividad de pesca ilegal detectada "
                "en área protegida",
                metadata={"sensor_data": result.get("sensor_data")}
            )
            await alert_service.send_alert(alert_obj, channels=['log'])

        return {
            "success": True,
            "data": result,
            "message": f"Análisis completado para {marine_region}"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error detectando actividad de pesca. "
            "Verifica la región."
        }


@tool
async def monitor_wildlife(
    park_name: str,
    species: Optional[str] = None
) -> dict:
    """
    Monitorea actividad de vida silvestre mediante cámaras trampa.

    Args:
        park_name: Nombre del parque nacional (ej: "Serengeti", "Kruger",
        "Yasuní")
        species: Especie específica a monitorear (opcional)

    Returns:
        Dict con análisis de actividad wildlife y detección de amenazas
    """
    try:
        if species:
            # Monitoreo específico por especie
            result = await wildlife_service.get_species_activity(
                park_name, species
            )
            return {
                "success": True,
                "data": result,
                "message": f"Actividad de {species} en {park_name}"
            }
        else:
            # Análisis general del parque
            result = await wildlife_service.analyze_camera_traps(park_name)

            # Generar alerta si hay actividad de caza furtiva
            if result.get("assessment", {}).get("alerts"):
                for alert in result["assessment"]["alerts"]:
                    if alert.get("type") == "POTENTIAL_POACHING":
                        alert_obj = alert_service.create_alert(
                            alert_type=AlertType.POACHING_ACTIVITY,
                            severity=AlertSeverity.HIGH,
                            location={"name": result["location"]["park"]},
                            description=alert.get(
                                "description", "Actividad sospechosa detectada"
                            ),
                            metadata={"camera_data": result.get(
                                "camera_analysis"
                            )}
                        )
                        await alert_service.send_alert(alert_obj, channels=[
                            'log'
                        ])

            return {
                "success": True,
                "data": result,
                "message": f"Monitoreo completado para {park_name}"
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error monitoreando vida silvestre. "
            "Verifica el nombre del parque."
        }


@tool
async def get_environmental_data(
    query: str,
    location: Optional[str] = None
) -> dict:
    """
    Obtiene datos ambientales generales (calidad del agua, aire, clima).

    Args:
        query: Tipo de dato solicitado (ej: "water quality", "air quality",
        "temperature")
        location: Ubicación opcional para filtrar datos

    Returns:
        Dict con datos ambientales relevantes
    """
    try:
        # Enrutamiento inteligente según el tipo de consulta
        query_lower = query.lower()

        if "water" in query_lower or "ocean" in query_lower or "marine" in query_lower:
            if location:
                result = await ocean_service.get_water_quality(location)
            else:
                result = {
                    "message": "Especifica coordenadas para"
                    "análisis de agua",
                    "example": "Lat: -0.75, Lon: -89.36"
                    }
        else:
            # Fallback: respuesta genérica con sugerencias
            result = {
                "message": f"Consulta recibida: '{query}'",
                "suggestions": [
                    "Para calidad de agua: usa 'water quality' + coordenadas",
                    "Para datos satelitales: usa analyze_deforestation",
                    "Para vida silvestre: usa monitor_wildlife"
                ],
                "location": location
            }

        return {
            "success": True,
            "data": result,
            "query": query
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error obteniendo datos ambientales."
        }


@tool
async def generate_conservation_report(
    topic: str,
    region: str,
    include_recommendations: bool = True
) -> dict:
    """
    Genera un reporte de conservación estructurado usando AI.

    Args:
        topic: Tema del reporte (ej: "deforestation trends",
                "endangered species")
        region: Región de interés
        include_recommendations: Si incluir recomendaciones de acción
            (default: True)

    Returns:
        Dict con reporte estructurado en markdown
    """
    try:
        from openai import AsyncOpenAI

        if not settings.OPENAI_API_KEY:
            return {
                "success": False,
                "error": "OPENAI_API_KEY no configurada",
                "message": "Configura tu API key en el archivo .env"
            }

        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        prompt = f"""
        Eres un experto en conservación de biodiversidad.
        Genera un reporte técnico
        pero accesible sobre: "{topic}" en la región: "{region}".

        Estructura requerida en markdown:
        # Reporte: {topic} - {region}

        ## 📊 Situación Actual
        [Análisis basado en datos disponibles]

        ## ⚠️ Principales Amenazas
        [Lista de amenazas identificadas]

        ## 🎯 Impacto en Biodiversidad
        [Especies/ecosistemas afectados]

        {"## 💡 Recomendaciones de Acción\\n[Acciones concretas para "
            "mitigación]" if include_recommendations else ""}

        ## 📈 Métricas Clave
        [Indicadores para monitoreo futuro]

        Usa datos realistas pero indica cuando sean estimaciones.
        Mantén el reporte en español, máximo 800 palabras.
        """

        response = await client.chat.completions.create(
            model=settings.AI_MODEL.replace("openai:", ""),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=settings.AI_MAX_TOKENS,
            temperature=settings.AI_TEMPERATURE
        )

        report_content = response.choices[0].message.content

        return {
            "success": True,
            "report": report_content,
            "metadata": {
                "topic": topic,
                "region": region,
                "generated_at": asyncio.get_event_loop().time(),
                "model_used": settings.AI_MODEL
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error generando reporte."
            "Verifica tu API key y conexión."
        }


@tool
async def check_alert_status(alert_id: Optional[str] = None) -> dict:
    """
    Consulta el estado de alertas activas o una alerta específica por ID.

    Args:
        alert_id: ID de alerta específico (opcional).
        Si no se proporciona, retorna resumen.

    Returns:
        Dict con estado de alertas
    """
    # En una implementación completa, esto consultaría una base de datos
    # Aquí retornamos un estado simulado para modo demostración

    if alert_id:
        return {
            "alert_id": alert_id,
            "status": "MONITORING",  # Simulado
            "last_updated": asyncio.get_event_loop().time(),
            "message": f"Alerta {alert_id} en monitoreo activo"
        }
    else:
        return {
            "active_alerts_summary": {
                "total": 0,
                "by_severity": {
                    "critical": 0,
                    "high": 0,
                    "medium": 0,
                    "low": 0},
                "note": "Modo demostración: Las alertas se registran en consola. ""Configura persistencia para producción."
            },
            "message": "Sistema de alertas operativo. Usa alert_id para consultar una específica."
        }


@tool
async def search_biodiversity_database(
    query: str,
    category: Optional[str] = None
) -> dict:
    """
    Busca información en bases de datos de biodiversidad (simulado).

    Args:
        query: Término de búsqueda (especie, ecosistema, amenaza)
        category: Categoría opcional: 'species', 'ecosystem', 'threat', 'conservation'

    Returns:
        Dict con resultados de búsqueda
    """
    # Base de conocimiento simulada para demostración
    knowledge_base = {
        "jaguar": {
            "name": "Jaguar (Panthera onca)",
            "status": "Near Threatened",
            "habitat": "Américas: desde México hasta Argentina",
            "threats": ["Deforestación", "Caza furtiva", "Fragmentación de hábitat"],
            "conservation_actions": ["Corredores biológicos", "Protección de cuencas", "Monitoreo con cámaras trampa"]
        },
        "amazon rainforest": {
            "name": "Amazon Rainforest",
            "type": "Tropical Rainforest Ecosystem",
            "area_km2": 5500000,
            "biodiversity": "~10% de todas las especies conocidas del planeta",
            "threats": ["Deforestación agrícola", "Minería ilegal", "Cambio climático"],
            "conservation_actions": ["Áreas protegidas", "Monitoreo satelital", "Desarrollo sostenible con comunidades"]
        },
        "coral reef": {
            "name": "Coral Reefs",
            "type": "Marine Ecosystem",
            "global_coverage": "0.1% del océano, pero alberga ~25% de especies marinas",
            "threats": ["Blanqueamiento por calentamiento", "Acidificación oceánica", "Contaminación"],
            "conservation_actions": ["Áreas marinas protegidas", "Restauración de corales", "Reducción de emisiones"]
        }
    }

    query_lower = query.lower()
    results = []

    for key, value in knowledge_base.items():
        if query_lower in key or (category and category.lower() in key):
            results.append(value)

    if not results:
        return {
            "success": True,
            "results": [],
            "message": f"No se encontraron resultados para '{query}'. Prueba con: 'jaguar', 'amazon', 'coral reef'",
            "suggestion": "Usa términos en inglés para mejores resultados en esta demo"
        }

    return {
        "success": True,
        "results": results,
        "query": query,
        "category": category,
        "message": f"{len(results)} resultado(s) encontrado(s)"
    }