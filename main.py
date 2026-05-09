import os
from dotenv import load_dotenv
from loguru import logger
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import uvicorn

load_dotenv()

app = FastAPI(title="Agentic Nexus Lab API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

def initialize_lab():
    logger.info("Initializing Agentic Nexus Lab...")
    log_level = os.getenv("LOG_LEVEL", "INFO")
    logger.info(f"Log level: {log_level}")
    logger.info("LLM Council + Agent Enterprise Team ready.")

@app.get("/")
async def read_index():
    index_path = os.path.join(BASE_PATH, "index.html")
    if not os.path.exists(index_path):
        logger.error(f"index.html not found at {index_path}")
        raise HTTPException(status_code=404, detail="index.html not found at project root")
    return FileResponse(index_path)

@app.get("/health")
async def health():
    return JSONResponse({"status": "online", "lab": "Agentic Nexus Lab"})

@app.get("/api/council/status")
async def council_status():
    return JSONResponse({
        "council": [
            {"name": "Claude Opus", "provider": "anthropic", "role": "Strategist", "status": "ready"},
            {"name": "GPT-4o", "provider": "openai", "role": "Analyst", "status": "ready"},
            {"name": "Gemini Ultra", "provider": "google", "role": "Researcher", "status": "ready"},
        ],
        "consensus_mode": "weighted_vote"
    })

@app.get("/api/agents/status")
async def agents_status():
    return JSONResponse({
        "agents": [
            {"name": "Nexus-CEO", "role": "Orchestrator", "status": "active"},
            {"name": "Nexus-Research", "role": "Researcher", "status": "standby"},
            {"name": "Nexus-Code", "role": "Engineer", "status": "standby"},
            {"name": "Nexus-Strategy", "role": "Strategist", "status": "standby"},
            {"name": "Nexus-Ethics", "role": "Alignment", "status": "standby"},
        ]
    })

def run_server():
    initialize_lab()
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Dashboard: http://localhost:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)

if __name__ == "__main__":
    run_server()