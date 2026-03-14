import asyncio
from fastapi import Request
from pydantic_ai.ag_ui import RunAgentInput, AGUIAdapter
from agent import agent

async def test():
    data = {
        "method": "agent/run",
        "params": {"agentId": "default"},
        "body": {
            "threadId": "a9e8ae21",
            "runId": "1c9ef718",
            "tools": [],
            "context": [],
            "forwardedProps": {},
            "state": {},
            "messages": [
                {"id": "cb49", "content": "dasdasd", "role": "user"}
            ]
        }
    }
    
    async def mock_receive():
        return {"type": "http.request", "body": b'{"method": "agent/run"}'}
        
    request = Request({"type": "http", "method": "POST"}, mock_receive)
    body = await request.body()
    print("Initial body:", body)
    
    # Simulate our main.py rewrite
    run_input = RunAgentInput.model_validate(data["body"])
    json_bytes = run_input.model_dump_json().encode("utf-8")
    
    # We must clear the cached body and override receive again
    request._body = json_bytes
    
    async def new_receive():
        return {"type": "http.request", "body": json_bytes}
    request._receive = new_receive
    
    new_body = await request.body()
    print("New body:", new_body)

asyncio.run(test())
