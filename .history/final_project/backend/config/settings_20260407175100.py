"""
Configuración centralizada del proyecto.
Gestiona variables de entorno, claves API y parámetros del sistema.
"""
import os
from dotenv import load_dotenv


# Cargar variables de entorno
load_dotenv()


class Settings:
    """Configuración global de la aplicación."""

    # ===============================
    # CONFIGURACIÓN DE API KEYS
    # ===============================
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # APIs externas para datos reales (opcionales)
    NASA_EARTHDATA_API_KEY: str = os.getenv("NASA_EARTHDATA_API_KEY", "")
    OCEAN_OBSERVATORY_API_KEY: str = os.getenv("OCEAN_OBSERVATORY_API_KEY", "")
    WILDLIFE_CAMS_API_KEY: str = os.getenv("WILDLIFE_CAMS_API_KEY", "")

    # ===============================
    # CONFIGURACIÓN DEL MODELO AI
    # ===============================
    AI_MODEL: str = os.getenv("AI_MODEL", "openai:gpt-4o-mini")
    AI_TEMPERATURE: float = float(os.getenv("AI_TEMPERATURE", "0.7"))
    AI_MAX_TOKENS: int = int(os.getenv("AI_MAX_TOKENS", "2048"))

    # ===============================
    # CONFIGURACIÓN DEL SERVIDOR
    # ===============================
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # ===============================
    # RATE LIMITING
    # ===============================
    RATE_LIMIT: int = int(os.getenv("RATE_LIMIT", "30"))
    RATE_WINDOW: int = int(os.getenv("RATE_WINDOW", "60"))

    # ===============================
    # CORS
    # ===============================
    ALLOWED_ORIGINS: list[str] = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")

    # ===============================
    # SEGURIDAD
    # ===============================
    MAX_MESSAGE_LENGTH: int = int(os.getenv("MAX_MESSAGE_LENGTH", "2000"))

    # ===============================
    # VALIDACIÓN
    # ===============================
    @classmethod
    def validate(cls) -> bool:
        """Valida que las configuraciones críticas estén presentes."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY no está configurada en el .env")

        if not cls.AI_MODEL.startswith("openai:"):
            print(f"⚠️ Advertencia: El modelo actual es {cls.AI_MODEL}")
            print("Se recomienda usar openai:gpt-4o-mini o "
                   "openai:gpt-4-turbo")

        return True

    @classmethod
    def is_production_ready(cls) -> bool:
        """Verifica si la configuración es adecuada para producción."""
        return (
            cls.OPENAI_API_KEY != "" and
            not cls.DEBUG and
            cls.RATE_LIMIT > 0
        )


# Instancia global de configuración
settings = Settings()
