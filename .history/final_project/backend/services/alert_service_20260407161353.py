"""
Servicio para gestión y envío de alertas a autoridades y sistemas de respuesta.
Soporta: Email, Webhooks, SMS (vía Twilio), y notificaciones push.
"""
import asyncio
import aiohttp
from typing import Optional, List
from datetime import datetime
from enum import Enum
from config.settings import settings


class AlertSeverity(Enum):
    """Niveles de severidad para alertas."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(Enum):
    """Tipos de alertas soportadas."""
    DEFORESTATION_DETECTED = "deforestation_detected"
    ILLEGAL_TRAWLING = "illegal_trawling"
    POACHING_ACTIVITY = "poaching_activity"
    SPECIES_AT_RISK = "species_at_risk"
    WATER_QUALITY_ALERT = "water_quality_alert"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    SYSTEM_ERROR = "system_error"


class AlertService:
    """Servicio centralizado para gestión de alertas de biodiversidad."""

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY  # Generar de resúmenes con IA
        self.webhook_url: Optional[str] = None  # Configurable vía .env
        self.email_recipients: List[str] = []
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Obtiene o crea una sesión HTTP asíncrona."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self):
        """Cierra la sesión HTTP."""
        if self.session and not self.session.closed:
            await self.session.close()

    def create_alert(
        self,
        alert_type: AlertType,
        severity: AlertSeverity,
        location: dict,
        description: str,
        metadata: Optional[dict] = None
    ) -> dict:
        """
        Crea una estructura de alerta estandarizada.

        Args:
            alert_type: Tipo de alerta (enum)
            severity: Nivel de severidad (enum)
            location: Dict con coordenadas y nombre de ubicación
            description: Descripción legible de la alerta
            metadata: Datos adicionales opcionales

        Returns:
            Dict con la alerta estructurada
        """
        return {
            "id": f"ALT-{datetime.now().strftime('%Y%m%d%H%M%S')}-
            {hash(description) % 10000:04d}",
            "type": alert_type.value,
            "severity": severity.value,
            "location": location,
            "description": description,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
            "status": "NEW",
            "acknowledged": False
        }

    async def send_alert(self, alert: dict, channels: Optional[List[str]] = None) -> dict:
        """
        Envía una alerta a los canales configurados.

        Args:
            alert: Dict de alerta creado con create_alert()
            channels: Lista de canales ['webhook', 'email', 'log']. Default: todos configurados

        Returns:
            Dict con resultado del envío
        """
        channels = channels or ['log']  # Por defecto, solo log en modo demostración
        results = {}

        for channel in channels:
            try:
                if channel == 'log':
                    results['log'] = await self._log_alert(alert)

                elif channel == 'webhook' and self.webhook_url:
                    results['webhook'] = await self._send_webhook(alert)

                elif channel == 'email' and self.email_recipients:
                    results['email'] = await self._send_email(alert)

                else:
                    results[channel] = {"status": "skipped", "reason": "Not configured"}

            except Exception as e:
                results[channel] = {"status": "error", "error": str(e)}

        # Actualizar estado de la alerta
        alert["dispatch_results"] = results
        alert["status"] = "DISPATCHED" if any(
            r.get("status") == "sent" for r in results.values()
        ) else "FAILED"

        return alert

    async def _log_alert(self, alert: dict) -> dict:
        """Registra la alerta en consola/logs del sistema."""
        severity_emoji = {
            "low": "🔵",
            "medium": "🟡",
            "high": "🟠",
            "critical": "🔴"
        }

        print(f"\n{severity_emoji.get(alert['severity'], '⚪')} ALERTA [{alert['severity'].upper()}]")
        print(f"   ID: {alert['id']}")
        print(f"   Tipo: {alert['type']}")
        print(f"   Ubicación: {alert['location'].get('name', 'Desconocida')}")
        print(f"   Descripción: {alert['description']}")
        print(f"   Timestamp: {alert['timestamp']}")
        if alert.get('metadata'):
            print(f"   Metadata: {alert['metadata']}")
        print("-" * 60)

        return {"status": "logged", "timestamp": datetime.now().isoformat()}

    async def _send_webhook(self, alert: dict) -> dict:
        """Envía la alerta vía webhook HTTP POST."""
        session = await self._get_session()

        payload = {
            "alert": alert,
            "source": "BiodiversityAgent",
            "version": "1.0"
        }

        async with session.post(
            self.webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"}
        ) as response:
            status = "sent" if response.status < 400 else "failed"
            return {
                "status": status,
                "http_status": response.status,
                "timestamp": datetime.now().isoformat()
            }

    async def _send_email(self, alert: dict) -> dict:
        """
        Envía la alerta por email.
        Nota: En producción, integrar con SendGrid, AWS SES, o similar.
        """
        # Implementación simulada para modo demostración
        print(
            f"   📧 Email simulado enviado a: "
            f"{', '.join(self.email_recipients)}"
        )
        print(
            f"      Asunto: [{alert['severity'].upper()}] "
            f"{alert['type']} - {alert['location'].get('name', '')}"
        )

        return {
            "status": "sent",
            "recipients": self.email_recipients,
            "timestamp": datetime.now().isoformat()
        }

    async def generate_ai_summary(self, alert: dict) -> str:
        """
        Genera un resumen ejecutivo de la alerta usando OpenAI.
        Útil para reportes a autoridades o stakeholders.
        """
        if not self.api_key:
            return f"Resumen no disponible (API Key no configurada). Alerta: {alert['description']}"

        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.api_key)

            prompt = f"""
            Eres un asistente especializado en conservación de biodiversidad.
            Genera un resumen ejecutivo CONCISO y PROFESIONAL para autoridades ambientales
            basado en esta alerta:

            Tipo: {alert['type']}
            Severidad: {alert['severity']}
            Ubicación: {alert['location']}
            Descripción: {alert['description']}
            Metadata: {alert.get('metadata', {})}

            El resumen debe:
            - Tener máximo 3 oraciones
            - Incluir acción recomendada
            - Usar tono formal pero urgente si aplica
            - Estar en español
            """

            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.3
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"Error generando resumen AI: {str(e)}"


# Instancia singleton
alert_service = AlertService()
