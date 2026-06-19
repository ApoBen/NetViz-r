import os
import sys
import typing

# Python 3.12.4+ / 3.13 compatibility monkeypatch for Pydantic V1
if sys.version_info >= (3, 12, 4):
    original_evaluate = typing.ForwardRef._evaluate
    def patched_evaluate(self, globalns, localns, type_params=None, recursive_guard=None):
        if recursive_guard is None:
            if isinstance(type_params, set):
                recursive_guard = type_params
                type_params = None
            else:
                recursive_guard = set()
        return original_evaluate(self, globalns, localns, type_params=type_params, recursive_guard=recursive_guard)
    typing.ForwardRef._evaluate = patched_evaluate

import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.websocket_manager import manager
from app.logger import Logger

# Monitors
from app.monitors.bandwidth import monitor_bandwidth
from app.monitors.connections import monitor_connections
from app.monitors.processes import monitor_processes

app = FastAPI(title="NetVizör Backend")
global_logger = Logger()

# Check if running as root / admin
try:
    IS_ROOT = os.geteuid() == 0
except AttributeError:
    # Windows fallback
    import ctypes
    try:
        IS_ROOT = ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        IS_ROOT = False

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")

# Mount frontend static files
if os.path.exists(frontend_dir):
    app.mount("/css", StaticFiles(directory=os.path.join(frontend_dir, "css")), name="css")
    app.mount("/js", StaticFiles(directory=os.path.join(frontend_dir, "js")), name="js")

@app.get("/")
async def root():
    return FileResponse(os.path.join(frontend_dir, "index.html"))

@app.get("/api/status")
async def get_status():
    return {
        "mode": "Advanced (Root)" if IS_ROOT else "Basic (Non-Root)",
        "is_paused": global_logger.is_paused
    }

@app.post("/api/pause")
async def pause_monitoring():
    global_logger.pause()
    return {"status": "paused"}

@app.post("/api/resume")
async def resume_monitoring():
    global_logger.resume()
    return {"status": "resumed"}

@app.post("/api/export")
async def export_data():
    try:
        filename = global_logger.export_json()
        return {"status": "success", "file": filename}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.post("/api/clear")
async def clear_data():
    global_logger.clear_data()
    return {"status": "cleared"}

from pydantic import BaseModel
class WhitelistRequest(BaseModel):
    app_name: str

@app.post("/api/whitelist")
async def add_whitelist(req: WhitelistRequest):
    from app.monitors.security import security_manager
    security_manager.whitelisted_apps.add(req.app_name)
    return {"status": "success", "app": req.app_name}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, listen for client messages if any
            data = await websocket.receive_text()
            # client messages can be handled here (e.g. pause/resume commands over ws)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.on_event("startup")
async def startup_event():
    # Start basic monitors
    asyncio.create_task(monitor_bandwidth(global_logger))
    asyncio.create_task(monitor_connections(global_logger))
    asyncio.create_task(monitor_processes(global_logger))
    
    # Start advanced monitors if root
    if IS_ROOT:
        from app.monitors.packets import monitor_packets
        from app.monitors.dns_tracker import monitor_dns
        asyncio.create_task(monitor_packets(global_logger))
        asyncio.create_task(monitor_dns(global_logger))
        print("Running in ADVANCED mode (Root). All monitors active.")
    else:
        print("Running in BASIC mode (Non-Root). Packet and DNS capture disabled.")
