import psutil
import time
import asyncio
from collections import defaultdict
from app.websocket_manager import manager
from app.logger import Logger
from app.monitors.security import security_manager

async def monitor_processes(logger: Logger):
    last_io = {}
    last_time = time.time()
    
    while True:
        try:
            current_time = time.time()
            time_elapsed = current_time - last_time
            
            pid_connections = defaultdict(int)
            try:
                for conn in psutil.net_connections(kind='inet'):
                    if conn.pid:
                        pid_connections[conn.pid] += 1
            except (psutil.AccessDenied, PermissionError):
                pass
            
            processes_data = []
            
            try:
                for p in psutil.process_iter(['pid', 'name', 'username', 'io_counters']):
                    try:
                        pid = p.info['pid']
                        name = p.info['name']
                        
                        if pid in pid_connections:
                            io = p.info['io_counters']
                            
                            upload_speed = 0
                            download_speed = 0
                            
                            if io and pid in last_io:
                                last = last_io[pid]
                                upload_speed = max(0, (io.write_bytes - last.write_bytes) / time_elapsed)
                                download_speed = max(0, (io.read_bytes - last.read_bytes) / time_elapsed)
                                
                            if io:
                                last_io[pid] = io
                                
                            # Security Check for Spikes
                            current_total_bps = upload_speed + download_speed
                            await security_manager.detect_bandwidth_spike(pid, name, current_total_bps, logger)
                                
                            processes_data.append({
                                "pid": pid,
                                "name": name,
                                "user": p.info['username'],
                                "connections": pid_connections[pid],
                                "upload_speed_bps": upload_speed,
                                "download_speed_bps": download_speed,
                                "total_sent": io.write_bytes if io else 0,
                                "total_recv": io.read_bytes if io else 0
                            })
                    except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                        pass
            except (psutil.AccessDenied, PermissionError):
                pass
            
            processes_data.sort(key=lambda x: x['upload_speed_bps'] + x['download_speed_bps'], reverse=True)
            
            payload = {
                "type": "processes",
                "data": {
                    "processes": processes_data[:20]
                }
            }
            
            logger.log_data("processes", payload["data"])
            await manager.broadcast(payload)
            
            last_time = current_time
            
        except Exception as e:
            pass
            
        await asyncio.sleep(3)
