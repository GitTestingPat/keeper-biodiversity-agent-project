"""Agente con LangChain - Versión corregida"""
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from config.settings import settings
from tools import TOOLS_REGISTRY


def create_agent():
    """Crea un agente que puede usar herramientas y EJECUTARLAS"""

    settings.validate()

    llm = ChatOpenAI(
        model=settings.AI_MODEL.replace("openai:", ""),
        temperature=settings.AI_TEMPERATURE,
        api_key=settings.OPENAI_API_KEY,
        streaming=True
    )

    # Extraer la lista de herramientas del registry
    # Asumimos que TOOLS_REGISTRY tiene una clave 'tools' con la lista
    tools = TOOLS_REGISTRY.get("tools", []) if isinstance(TOOLS_REGISTRY, dict) else TOOLS_REGISTRY

    # Prompt para el agente
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Eres un experto en biodiversidad y conservación. "
            "Usa las herramientas disponibles para responder con datos 
            precisos. "
            "Responde en español."),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    # Crear el agente que llama a herramientas
    agent = create_tool_calling_agent(llm, tools, prompt)

    # Crear el ejecutor que realmente corre el agente
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,  # Muestra logs en consola
        handle_parsing_errors=True,  # Evita que se cuelgue por errores de parseo
        max_iterations=3,  # Evita bucles infinitos
        return_intermediate_steps=False
    )

    return agent_executor


# Instancia global del agente listo para usar
agent = create_agent()