import os
import sys
import typing

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

if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS
else:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

frontend_dir = os.path.join(base_dir, "frontend")

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

@app.get("/api/settings")
async def get_settings():
    return {
        "sql_enabled": getattr(global_logger, "sql_enabled", False)
    }

class SqlSettingRequest(BaseModel):
    enabled: bool

@app.post("/api/settings/sql")
async def set_sql_setting(req: SqlSettingRequest):
    global_logger.toggle_sql(req.enabled)
    return {"status": "success", "sql_enabled": global_logger.sql_enabled}

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
        await manager.disconnect(websocket)

@app.on_event("startup")
async def startup_event():
    # Start basic monitors
    asyncio.create_task(monitor_bandwidth(global_logger))
    asyncio.create_task(monitor_connections(global_logger))
    asyncio.create_task(monitor_processes(global_logger))
    
    # Start advanced monitors if root
    if IS_ROOT:
        has_raw_sockets = True
        try:
            import socket
            if os.name == 'posix':
                s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
                s.close()
        except Exception as e:
            has_raw_sockets = False
            print(f"Uyari: Root yetkisi var ancak ham soket (raw socket) izni yok. ({e})")
            print("Termux veya kisitli bir ortamda olabilirsiniz.")
            
        if has_raw_sockets:
            from app.monitors.packets import monitor_packets
            from app.monitors.dns_tracker import monitor_dns
            asyncio.create_task(monitor_packets(global_logger))
            asyncio.create_task(monitor_dns(global_logger))
            print("Running in ADVANCED mode (Root). All monitors active.")
        else:
            print("Running in BASIC mode (Root, but no raw socket permission). Packet and DNS capture disabled.")
    else:
        print("Running in BASIC mode (Non-Root). Packet and DNS capture disabled.")
