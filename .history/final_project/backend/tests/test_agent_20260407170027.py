"""
Tests unitarios para el agente de biodiversidad.
Ejecutar: pytest backend/tests/ -v
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from config.settings import Settings


class TestSettings:
    """Tests para la configuración del sistema."""

    def test_settings_validation_missing_key(self):
        """Debe fallar si OPENAI_API_KEY no está configurada."""
        with patch.dict('os.environ', {}, clear=True):
            settings = Settings()
            with pytest.raises(ValueError, match="OPENAI_API_KEY"):
                settings.validate()

    def test_settings_validation_success(self):
        """Debe pasar si OPENAI_API_KEY está presente."""
        with patch.dict('os.environ', {
            'OPENAI_API_KEY': 'test-key-123',
            'AI_MODEL': 'openai:gpt-4o-mini'
        }):
            settings = Settings()
            assert settings.validate() is True
            assert settings.OPENAI_API_KEY == 'test-key-123'

    def test_is_production_ready(self):
        """Verifica lógica de readiness para producción."""
        with patch.dict('os.environ', {
            'OPENAI_API_KEY': 'prod-key',
            'DEBUG': 'False',
            'RATE_LIMIT': '100'
        }):
            settings = Settings()
            assert settings.is_production_ready() is True

        # Debe fallar si DEBUG está activo
        with patch.dict('os.environ', {
            'OPENAI_API_KEY': 'prod-key',
            'DEBUG': 'True',  # ← Esto hace que falle
            'RATE_LIMIT': '100'
        }):
            settings = Settings()
            assert settings.is_production_ready() is False


class TestBiodiversityTools:
    """Tests para las herramientas del agente (mockeados)."""

    @pytest.mark.asyncio
    async def test_analyze_deforestation_mock(self):
        """Test de herramienta con servicio mockeado."""
        from tools.biodiversity_tools import analyze_deforestation

        # Mockear el servicio de satélites
        with patch('tools.biodiversity_tools.satellite_service') as 
        mock_satellite:
            mock_satellite.analyze_region = AsyncMock(return_value={
                "forest_cover_change": {"change_percent": -2.5},
                "alerts": []
            })

            result = await analyze_deforestation("Amazonas")

            assert result["success"] is True
            assert "data" in result
            mock_satellite.analyze_region.assert_called_once_with("Amazonas")

    @pytest.mark.asyncio
    async def test_detect_illegal_fishing_protected_area(self):
        """Test de detección de pesca ilegal en área protegida."""
        from tools.biodiversity_tools import detect_illegal_fishing

        with patch('tools.biodiversity_tools.ocean_service') as mock_ocean:
            mock_ocean.detect_illegal_trawling = AsyncMock(return_value={
                "assessment": {
                    "is_protected_area": True,
                    "risk_level": "HIGH"
                },
                "location": {"region": "Galapagos"}
            })

            with patch('tools.biodiversity_tools.alert_service') as mock_alerts:
                mock_alerts.create_alert = MagicMock()
                mock_alerts.send_alert = AsyncMock()

                result = await detect_illegal_fishing("Galapagos")

                assert result["success"] is True
                # Verificar que se creó alerta para área protegida con riesgo alto
                mock_alerts.create_alert.assert_called_once()


class TestAlertService:
    """Tests para el servicio de alertas."""

    def test_create_alert_structure(self):
        """Verifica que las alertas tengan la estructura correcta."""
        from services.alert_service import alert_service, AlertType, AlertSeverity

        alert = alert_service.create_alert(
            alert_type=AlertType.DEFORESTATION_DETECTED,
            severity=AlertSeverity.HIGH,
            location={"name": "Test Park"},
            description="Test description"
        )

        assert alert["id"].startswith("ALT-")
        assert alert["type"] == "deforestation_detected"
        assert alert["severity"] == "high"
        assert alert["status"] == "NEW"
        assert alert["acknowledged"] is False

    @pytest.mark.asyncio
    async def test_send_alert_log_channel(self):
        """Test de envío de alerta al canal de log."""
        from services.alert_service import alert_service, AlertType, AlertSeverity

        alert = alert_service.create_alert(
            alert_type=AlertType.SYSTEM_ERROR,
            severity=AlertSeverity.LOW,
            location={"name": "Test"},
            description="Test alert"
        )

        result = await alert_service.send_alert(alert, channels=['log'])

        assert result["status"] == "DISPATCHED"
        assert "log" in result["dispatch_results"]
        assert result["dispatch_results"]["log"]["status"] == "logged"


# Configurar pytest-asyncio
pytest_plugins = ('pytest_asyncio',)