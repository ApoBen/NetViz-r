import psutil
import asyncio
from app.websocket_manager import manager
from app.logger import Logger
from app.monitors.security import security_manager

async def monitor_connections(logger: Logger):
    while True:
        try:
            try:
                connections = psutil.net_connections(kind='inet')
            except (psutil.AccessDenied, PermissionError):
                # Termux / Strict environments without root
                connections = []
            
            conn_list = []
            status_counts = {}
            
            for conn in connections:
                laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A"
                raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A"
                
                status = conn.status
                status_counts[status] = status_counts.get(status, 0) + 1
                
                proc_name = "Bilinmeyen"
                if conn.pid:
                    try:
                        proc = psutil.Process(conn.pid)
                        proc_name = proc.name()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                        
                conn_list.append({
                    "fd": conn.fd,
                    "family": "IPv4" if conn.family == 2 else ("IPv6" if conn.family == 10 else str(conn.family)),
                    "type": "TCP" if conn.type == 1 else ("UDP" if conn.type == 2 else str(conn.type)),
                    "laddr": laddr,
                    "raddr": raddr,
                    "status": status,
                    "pid": conn.pid,
                    "process_name": proc_name
                })
                
            # Security Check
            await security_manager.check_suspicious_ports(conn_list, logger)
                
            payload = {
                "type": "connections",
                "data": {
                    "total": len(conn_list),
                    "status_counts": status_counts,
                    "connections": conn_list
                }
            }
            
            logger.log_data("connections", payload["data"])
            await manager.broadcast(payload)
            
        except Exception as e:
            # Silently handle global errors to keep thread alive on Termux
            pass
            
        await asyncio.sleep(2)
