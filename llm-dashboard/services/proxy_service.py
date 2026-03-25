import time
import uuid
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
from config.database import db
from llm_models import UsageLogModel
from datetime import datetime

app = FastAPI(title="LLM Token Dashboard Proxy")

OPENAI_BASE_URL = "https://api.openai.com"

PRICING = {
    "gpt-4o": {
        "input":  0.000005,
        "output": 0.000015
    },
    "gpt-4o-mini": {
        "input":  0.00000015,
        "output": 0.0000006
    },
    "gpt-3.5-turbo": {
        "input":  0.0000005,
        "output": 0.0000015
    },
    "gpt-4-turbo": {
        "input":  0.00001,
        "output": 0.00003
    }
}

def calculate_cost(model: str,
                   input_tokens: int,
                   output_tokens: int) -> float:
    pricing = PRICING.get(model, {
        "input": 0.000005,
        "output": 0.000015
    })
    return round(
        input_tokens  * pricing["input"] +
        output_tokens * pricing["output"],
        6
    )

def detect_call_type(body: dict,
                     custom_call_type: str = None) -> str:
    if custom_call_type:
        return custom_call_type

    tools      = body.get("tools", [])
    max_tokens = body.get("max_tokens", 0)
    model      = body.get("model", "")
    temp       = body.get("temperature", 0.7)
    messages   = body.get("messages", [])
    resp_fmt   = body.get("response_format", {})

    if tools:
        return "tool_call"
    if resp_fmt.get("type") == "json_object":
        return "structured_output"
    if "gpt-4o" in model and max_tokens >= 3000:
        return "heavy_analysis"
    if max_tokens >= 1000:
        return "medium_call"
    if temp <= 0.1:
        return "deterministic_call"
    if len(messages) > 3:
        return "conversation"
    return "llm_call"

async def log_to_supabase(
    project_id:    str,
    api_key_id:    str,
    session_id:    str,
    model:         str,
    call_type:     str,
    input_tokens:  int,
    output_tokens: int,
    cost_usd:      float,
    latency_ms:    int,
    status:        str,
    temperature:   float,
    max_tokens:    int
):
    try:
        record = UsageLogModel(
            project_id=project_id,
            api_key_id=api_key_id,
            session_id=session_id,
            provider="openai",
            model=model,
            tier="paid",
            call_type=call_type,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
            status=status,
            temperature=temperature,
            max_tokens_set=max_tokens,
            timestamp=datetime.utcnow()
        )
        db.client.table("usage_logs").insert(
            record.to_dict()
        ).execute()
        print(f"✅ Logged: {call_type} → {model} → ${cost_usd}")
    except Exception as e:
        print(f"❌ Logging error: {e}")

@app.post("/proxy/openai/{path:path}")
async def proxy_openai(path: str, request: Request):
    start_time = time.time()

    project_id       = request.headers.get("X-Project-ID")
    api_key_id       = request.headers.get("X-API-Key-ID")
    session_id       = request.headers.get(
                           "X-Session-ID",
                           str(uuid.uuid4())
                       )
    custom_call_type = request.headers.get("X-Call-Type")
    auth_header      = request.headers.get("Authorization", "")

    body = await request.json()

    model       = body.get("model", "unknown")
    temperature = body.get("temperature", 0.7)
    max_tokens  = body.get("max_tokens", 0)
    call_type   = detect_call_type(body, custom_call_type)

    headers = {
        "Authorization": auth_header,
        "Content-Type":  "application/json"
    }

    target_url = f"{OPENAI_BASE_URL}/v1/{path}"

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                target_url,
                json=body,
                headers=headers
            )

        latency_ms    = int((time.time() - start_time) * 1000)
        response_data = response.json()

        input_tokens  = 0
        output_tokens = 0
        status        = "success"

        if response.status_code == 200:
            usage         = response_data.get("usage", {})
            input_tokens  = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
        else:
            status = f"error_{response.status_code}"

        cost_usd = calculate_cost(
            model,
            input_tokens,
            output_tokens
        )

        await log_to_supabase(
            project_id=project_id,
            api_key_id=api_key_id,
            session_id=session_id,
            model=model,
            call_type=call_type,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
            status=status,
            temperature=temperature,
            max_tokens=max_tokens
        )

        short_session = session_id[:8] if session_id else "no-session"
        print(
            f"📊 [{short_session}] {call_type} | {model} | "
            f"{input_tokens + output_tokens} tokens | "
            f"${cost_usd} | {latency_ms}ms"
        )
        
        return JSONResponse(
            content=response_data,
            status_code=response.status_code
        )

    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        await log_to_supabase(
            project_id=project_id,
            api_key_id=api_key_id,
            session_id=session_id,
            model=model,
            call_type=call_type,
            input_tokens=0,
            output_tokens=0,
            cost_usd=0,
            latency_ms=latency_ms,
            status="error",
            temperature=temperature,
            max_tokens=max_tokens
        )
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/health")
async def health():
    return {
        "status":  "running",
        "proxy":   "LLM Token Dashboard",
        "version": "1.0.0"
    }