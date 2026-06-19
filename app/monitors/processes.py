import psutil
import socket
import asyncio
from collections import defaultdict
from app.websocket_manager import manager
from app.logger import Logger

async def monitor_processes(logger: Logger):
    while True:
        try:
            # Get all network connections grouped by PID
            pid_connections = defaultdict(list)
            try:
                for conn in psutil.net_connections(kind='inet'):
                    if conn.pid:
                        conn_info = {
                            "raddr": conn.raddr.ip if conn.raddr else None,
                            "rport": conn.raddr.port if conn.raddr else None,
                            "status": conn.status,
                            "type": "TCP" if conn.type == socket.SOCK_STREAM else ("UDP" if conn.type == socket.SOCK_DGRAM else str(conn.type))
                        }
                        pid_connections[conn.pid].append(conn_info)
            except (psutil.AccessDenied, PermissionError):
                pass

            processes_data = []

            for pid, connections in pid_connections.items():
                try:
                    proc = psutil.Process(pid)
                    name = proc.name()
                    try:
                        user = proc.username()
                    except (psutil.AccessDenied, KeyError):
                        user = "Unknown"

                    processes_data.append({
                        "name": name,
                        "pid": pid,
                        "user": user,
                        "connection_count": len(connections),
                        "connections": connections
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            # Sort by connection_count descending, limit to top 20
            processes_data.sort(key=lambda x: x['connection_count'], reverse=True)

            payload = {
                "type": "processes",
                "data": {
                    "processes": processes_data[:20]
                }
            }

            logger.log_data("processes", payload["data"])
            await manager.broadcast(payload)

        except Exception:
            pass

        await asyncio.sleep(3)
