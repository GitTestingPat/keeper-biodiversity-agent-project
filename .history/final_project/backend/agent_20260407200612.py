# final_project/backend/agent.py
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent  
from config.settings import settings
from tools import TOOLS_REGISTRY


def create_agent():
    settings.validate()

    llm = ChatOpenAI(
        model=settings.AI_MODEL.replace("openai:", ""),
        temperature=settings.AI_TEMPERATURE,
        api_key=settings.OPENAI_API_KEY,
    )

    tools = TOOLS_REGISTRY.get(
        "tools", []
        ) if isinstance(TOOLS_REGISTRY, dict) else TOOLS_REGISTRY

    # create_react_agent crea un agente completo que SABE ejecutar herramientas
    # No necesitas bucles manuales ni AgentExecutor viejo.
    agent_graph = create_react_agent(llm, tools)

    return agent_graph


agent = create_agent()
