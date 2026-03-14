import os
import time
import re
from collections import defaultdict, deque
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic_ai.ag_ui import AGUIAdapter
from agent import agent
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Biodiversity Agent API")


# ═══════════════════════════════════════════════════════
# 1. SECURITY HEADERS MIDDLEWARE
# ═══════════════════════════════════════════════════════
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds hardened HTTP security headers to every response."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )
        return response


app.add_middleware(SecurityHeadersMiddleware)


# ═══════════════════════════════════════════════════════
# 2. RATE LIMITER MIDDLEWARE
#    In-memory store: 30 requests / 60 seconds per IP.
#    For production, replace with Redis-backed limiter.
# ═══════════════════════════════════════════════════════
RATE_LIMIT = int(os.getenv("RATE_LIMIT", "30"))        # requests per window
RATE_WINDOW = int(os.getenv("RATE_WINDOW", "60"))       # seconds

_request_log: dict[str, deque] = defaultdict(deque)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory sliding-window rate limiter per client IP."""

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window = _request_log[client_ip]

        # Purge timestamps older than the window
        while window and window[0] < now - RATE_WINDOW:
            window.popleft()

        if len(window) >= RATE_LIMIT:
            retry_after = int(RATE_WINDOW - (now - window[0])) + 1
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please try again later."},
                headers={"Retry-After": str(retry_after)},
            )

        window.append(now)
        return await call_next(request)


app.add_middleware(RateLimitMiddleware)


# ═══════════════════════════════════════════════════════
# 3. CORS — tightened to known frontend origins
# ═══════════════════════════════════════════════════════
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════════
# 4. INPUT VALIDATION HELPERS
# ═══════════════════════════════════════════════════════
MAX_MESSAGE_LENGTH = 2000

# Server-side prompt-injection patterns (blocks the request)
INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|rules)", re.I),
    re.compile(r"system\s*:\s*", re.I),
    re.compile(r"\bdo\s+not\s+follow\b.*\brules\b", re.I),
    re.compile(r"\bjailbreak\b", re.I),
]


def validate_last_user_message(messages: list[dict]) -> str | None:
    """
    Validate the last user message.
    Returns an error string if invalid, None if OK.
    """
    user_messages = [m for m in messages if m.get("role") == "user"]
    if not user_messages:
        return None  # No user message to validate

    last_content = user_messages[-1].get("content", "")
    if isinstance(last_content, list):
        # Multi-part messages — extract text parts
        last_content = " ".join(
            p.get("text", "") for p in last_content if isinstance(p, dict)
        )

    if not last_content or not last_content.strip():
        return "Message cannot be empty."
    if len(last_content) > MAX_MESSAGE_LENGTH:
        return f"Message exceeds maximum length of {MAX_MESSAGE_LENGTH} characters."

    for pattern in INJECTION_PATTERNS:
        if pattern.search(last_content):
            print(f"[SECURITY] Blocked potential prompt injection from message: {last_content[:80]}...")
            return "Your message was flagged by our security system. Please rephrase your request."

    return None


# ═══════════════════════════════════════════════════════
# AG-UI ENDPOINT SETUP
# ═══════════════════════════════════════════════════════
from pydantic_ai.ag_ui import RunAgentInput

# The exact info response CopilotKit expects:
INFO_RESPONSE = {
    "agents": {
        "default": {
            "description": "Biodiversity Agent via Pydantic AI"
        }
    }
}


@app.get("/chat/info")
async def chat_info_endpoint():
    """CopilotKit discovery endpoint (GET transport)."""
    return INFO_RESPONSE


@app.post("/chat")
async def chat_endpoint(request: Request):
    """
    The AG-UI endpoint compatible with CopilotKit.
    CopilotKit sends {"method": "info"} or {"method": "agent/run", "body": {...}}
    """
    data = await request.json()

    # CopilotKit initialization
    if data.get("method") == "info":
        return INFO_RESPONSE

    # CopilotKit chat execution
    body = data.get("body", {})
    if not body:
        body = data  # Fallback if someone sends raw AGUI payload

    # Extract messages and validate
    messages = body.get("messages", [])

    # ── Input validation ──────────────────────────
    validation_error = validate_last_user_message(messages)
    if validation_error:
        return JSONResponse(
            status_code=400,
            content={"detail": validation_error},
        )

    # We need to give AGUIAdapter the exact input it expects
    run_input = RunAgentInput(
        runId=body.get("runId") or "default-run",
        threadId=body.get("threadId") or "default-thread",
        state=body.get("state") or {},
        context=body.get("context") or [],
        tools=body.get("tools") or [],
        forwardedProps=body.get("forwardedProps") or {},
        messages=messages or []
    )

    # Serialize to JSON and encode appropriately
    json_bytes = run_input.model_dump_json().encode("utf-8")

    # Temporarily override the request body with what AGUIAdapter expects
    async def mock_receive():
        return {"type": "http.request", "body": json_bytes}

    # Overwrite FastAPI's cached request body so it reads the new payload
    request._body = json_bytes
    request._receive = mock_receive

    return await AGUIAdapter.dispatch_request(request, agent=agent)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
