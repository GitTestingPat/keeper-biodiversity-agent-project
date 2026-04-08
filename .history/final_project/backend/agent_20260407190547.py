"""Agente simple con OpenAI + herramientas"""
from langchain_openai import ChatOpenAI
from config.settings import settings
from tools import TOOLS_REGISTRY


def create_agent():
    """Crea un LLM con herramientas vinculadas"""

    settings.validate()

    llm = ChatOpenAI(
        model=settings.AI_MODEL.replace("openai:", ""),
        temperature=settings.AI_TEMPERATURE,
        api_key=settings.OPENAI_API_KEY,
    )

    # Obtener herramientas del registry
    tools = TOOLS_REGISTRY.get(
        "tools", []
        ) if isinstance(TOOLS_REGISTRY, dict) else TOOLS_REGISTRY

    # Vincular herramientas al modelo (esto SÍ funciona en todas las versiones)
    return llm.bind_tools(tools)


agent = create_agent()