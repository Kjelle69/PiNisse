from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import httpx
import os

#VLLM_BASE = "http://192.168.50.51:8000/v1"

OLLAMA_BASE = "http://192.168.50.51:11434/v1"



app = FastAPI()

# Serve the main HTML page
@app.get("/")
async def serve_index():
    # Read the index.html file and return it
    with open(os.path.join("static", "index.html"), "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

# Define your API routes BEFORE mounting static files
@app.post("/api/chat")
async def chat(req: Request):
    data = await req.json()
    async with httpx.AsyncClient(timeout=None) as client:
        r = await client.post(f"{OLLAMA_BASE}/chat/completions", json=data)
    return JSONResponse(r.json())


@app.get("/api/models")
async def models():
    async with httpx.AsyncClient(timeout=None) as client:
        r = await client.get(f"{OLLAMA_BASE}/models")
    return JSONResponse(r.json())


@app.post("/api/ha/webhook/{hook_id}")
async def ha_webhook(hook_id: str, req: Request):
    body = await req.body()
    headers = {}

    if body:
        headers["Content-Type"] = req.headers.get("content-type", "application/json")
    # else: don't set Content-Type for empty body

    async with httpx.AsyncClient(timeout=10) as client:
        if body:
            r = await client.post(
                f"http://homeassistant.local:8123/api/webhook/{hook_id}",
                content=body,
                headers=headers
            )
        else:
            r = await client.post(
                f"http://homeassistant.local:8123/api/webhook/{hook_id}",
                headers=headers # No Content-Type header for empty body
            )

    return JSONResponse({"status": r.status_code})

# Mount static files at /static
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")