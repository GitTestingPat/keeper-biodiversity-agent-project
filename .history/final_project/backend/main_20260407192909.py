"""Backend con FastAPI + LangChain"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from config.settings import settings
from agent import agent
from tools import TOOLS_REGISTRY

app = FastAPI(title="Biodiversity Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


@app.post("/api/chat")
async def chat(req: ChatRequest):
    """Endpoint de chat que ejecuta el agente con
        herramientas (Bucle Manual)"""
    try:
        # Obtener las herramientas reales del registry
        tools_list = TOOLS_REGISTRY.get(
            "tools", []
            ) if isinstance(TOOLS_REGISTRY, dict) else TOOLS_REGISTRY
        # Crear un mapa nombre_herramienta -> funcion para ejecutarlas rápido
        tool_map = {tool.name: tool for tool in tools_list}

        messages = [HumanMessage(content=req.message)]

        # Bucle máximo de 3 pasos (para evitar bucles infinitos si falla)
        for _ in range(3):
            # A. Preguntar al LLM
            response = await agent.ainvoke(messages)

            # B. Si NO hay llamadas a herramientas, hemos terminado
            # (respuesta final)
            if not response.tool_calls:
                return {
                    "success": True,
                    "response": response.content,
                    "tool_calls": []
                }

            # C. Si HAY llamadas a herramientas, ejecutarlas
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]

                print(f"🛠️ Ejecutando herramienta: {tool_name} con args: {
                    tool_args
                    }")

                if tool_name in tool_map:
                    # Ejecutar la herramienta (asegúrate que sean async
                    # o usa asyncio.run)
                    tool_func = tool_map[tool_name]
                    try:
                        # Intentar ejecutar como async primero
                        if hasattr(tool_func, 'coroutine'):
                            result = await tool_func.ainvoke(tool_args)
                        else:
                            # Si es una función normal decorada con @tool,
                            # a veces necesita invoke directo
                            # Ojo: LangChain tools suelen ser runables.
                            # Si falla, prueba:
                            # result = await tool_func.arun(**tool_args)
                            result = await tool_func.ainvoke(tool_args)
                    except Exception as e:
                        result = f"Error ejecutando herramienta: {str(e)}"

                    # Añadir el resultado al historial de mensajes
                    messages.append(
                        ToolMessage(content=str(result), tool_call_id=tool_call["id"]))
                else:
                    messages.append(ToolMessage(content=f"Herramienta {tool_name} no encontrada", tool_call_id=tool_call["id"]))

        # Si salimos del bucle sin retornar, es que hubo un error o límite
        return {"success": False, "error": "El agente no pudo generar una respuesta final en los intentos permitidos."}

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


@app.get("/health")
async def health():
    return {"status": "healthy", "model": settings.AI_MODEL}


@app.get("/api/tools")
async def list_tools():
    """Lista las herramientas disponibles"""
    return {
        "tools": [
            {"name": t.name, "description": t.description}
            for t in TOOLS_REGISTRY if hasattr(
                t, 'name'
            )
        ]
    }

if __name__ == "__main__":
    import uvicorn
    print(f"🌱 Biodiversity Agent corriendo en http://{settings.HOST}:{
        settings.PORT}"
    )
    uvicorn.run(
        "main:app", host=settings.HOST, port=settings.PORT, reload=True
    )
