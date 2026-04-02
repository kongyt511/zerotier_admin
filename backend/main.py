import os
import sys

# Allow imports from backend/ dir
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from config import read_config, write_config
from routers import status, networks, members, peers

app = FastAPI(title="ZeroTier Admin")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(status.router, prefix="/api")
app.include_router(networks.router, prefix="/api/networks")
app.include_router(members.router, prefix="/api/networks/{nwid}/members")
app.include_router(peers.router, prefix="/api/peers")


@app.get("/api/config")
async def get_config():
    cfg = read_config()
    # Mask token for display
    token = cfg["zt_token"]
    return {
        "zt_url": cfg["zt_url"],
        "zt_token": token,
    }


@app.post("/api/config")
async def set_config(body: dict):
    cfg = write_config(body)
    return {"zt_url": cfg["zt_url"], "zt_token": cfg["zt_token"]}


# Serve built frontend in production
DIST = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.isdir(DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(DIST, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str):
        index = os.path.join(DIST, "index.html")
        return FileResponse(index)
