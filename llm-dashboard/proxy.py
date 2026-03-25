import uvicorn
from services.proxy_service import app

if __name__ == "__main__":
    print("═" * 50)
    print("  LLM Token Dashboard — Proxy")
    print("═" * 50)
    print("\n✅ Proxy running on http://localhost:8000")
    print("✅ Dashboard on  http://localhost:8050")
    print("\nPoint your project to:")
    print("  OpenAI → http://localhost:8000/proxy/openai")
    print("\nPress Ctrl+C to stop")
    print("═" * 50)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )