"""Agente con LangChain"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config.settings import settings
from tools import TOOLS_REGISTRY


def create_agent():
    """Crea un agente que puede usar herramientas"""

    settings.validate()

    llm = ChatOpenAI(
        model=settings.AI_MODEL.replace("openai:", ""),
        temperature=settings.AI_TEMPERATURE,
        api_key=settings.OPENAI_API_KEY,
        streaming=True
    )

    # Vincular herramientas al LLM (estándar de LangChain)
    return llm.bind_tools(TOOLS_REGISTRY)


agent = create_agent()
