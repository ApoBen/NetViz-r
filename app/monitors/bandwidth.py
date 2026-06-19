import psutil
import time
import asyncio
from app.websocket_manager import manager
from app.logger import Logger

async def monitor_bandwidth(logger: Logger):
    try:
        last_io = psutil.net_io_counters(pernic=True)
    except (psutil.AccessDenied, PermissionError, NotImplementedError):
        last_io = {}
    last_time = time.time()
    
    while True:
        await asyncio.sleep(1)
        try:
            current_io = psutil.net_io_counters(pernic=True)
        except (psutil.AccessDenied, PermissionError, NotImplementedError):
            current_io = {}
        current_time = time.time()
        
        time_elapsed = current_time - last_time
        
        if time_elapsed < 0.1:
            last_time = current_time
            last_io = current_io
            continue
        
        interfaces_data = {}
        total_upload_speed = 0
        total_download_speed = 0
        
        for nic, io in current_io.items():
            if nic in last_io:
                last = last_io[nic]
                
                upload_speed = (io.bytes_sent - last.bytes_sent) / time_elapsed
                download_speed = (io.bytes_recv - last.bytes_recv) / time_elapsed
                
                # Sadece aktif ağ arayüzlerini gönder (lo dahil edilebilir)
                interfaces_data[nic] = {
                    "upload_speed_bps": upload_speed,
                    "download_speed_bps": download_speed,
                    "total_sent": io.bytes_sent,
                    "total_recv": io.bytes_recv
                }
                
                # Exclude loopback and virtual interfaces from the total sum
                is_virtual = nic.lower() == 'lo' or any(nic.lower().startswith(x) for x in ['docker', 'veth', 'br-', 'virbr', 'tun', 'tap', 'vboxnet', 'vmnet', 'loopback'])
                if not is_virtual:
                    total_upload_speed += upload_speed
                    total_download_speed += download_speed
                
        payload = {
            "type": "bandwidth",
            "data": {
                "total_upload_speed_bps": total_upload_speed,
                "total_download_speed_bps": total_download_speed,
                "interfaces": interfaces_data
            }
        }
        
        logger.log_data("bandwidth", payload["data"])
        await manager.broadcast(payload)
        
        last_io = current_io
        last_time = current_time
