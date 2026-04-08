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
    """Endpoint de chat que ejecuta el agente con herramientas"""
    try:
        # Ejecutar el agente con el mensaje del usuario
        response = await agent.ainvoke([HumanMessage(content=req.message)])
        return {
            "success": True,
            "response": response.content if hasattr(
                response, 'content') else str(response),
            "tool_calls": getattr(response, 'tool_calls', [])
        }
    except Exception as e:
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
