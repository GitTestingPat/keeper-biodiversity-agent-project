"""Agente completo con LangChain"""
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from config.settings import settings
from tools import TOOLS_REGISTRY


def create_agent():
    """Crea un agente ejecutable completo"""

    settings.validate()

    llm = ChatOpenAI(
        model=settings.AI_MODEL.replace("openai:", ""),
        temperature=settings.AI_TEMPERATURE,
        api_key=settings.OPENAI_API_KEY,
    )

    # Obtener herramientas
    tools = TOOLS_REGISTRY.get(
        "tools", []) if isinstance(TOOLS_REGISTRY, dict) else TOOLS_REGISTRY

    if not tools:
        raise ValueError("No se encontraron herramientas en TOOLS_REGISTRY")

    # Prompt simple
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Eres un experto en biodiversidad. Usa las herramientas para obtener datos reales. Responde en español."),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    # Crear el agente estructurado
    agent = create_tool_calling_agent(llm, tools, prompt)

    # Crear el EJECUTOR (esto maneja el bucle de tool_calls -> tool_output -> final answer)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True, # Verás los pasos en la consola
        handle_parsing_errors=True,
        max_iterations=3
    )

    return agent_executor


# Instancia global
agent = create_agent()
