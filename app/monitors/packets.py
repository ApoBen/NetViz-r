import asyncio
import threading
from collections import deque
from scapy.all import AsyncSniffer, IP, TCP, UDP, ICMP
from app.websocket_manager import manager
from app.logger import Logger
from app.monitors.security import security_manager

packet_buffer = deque(maxlen=200)

protocol_stats = {
    "TCP": 0,
    "UDP": 0,
    "ICMP": 0,
    "Other": 0
}

# We need the main event loop to send async alerts from the sniff thread
main_loop = None

def packet_callback(packet):
    try:
        proto = "Other"
        src_ip = "N/A"
        dst_ip = "N/A"
        src_port = ""
        dst_port = ""
        
        if IP in packet:
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
            
            if TCP in packet:
                proto = "TCP"
                src_port = str(packet[TCP].sport)
                dst_port = str(packet[TCP].dport)
            elif UDP in packet:
                proto = "UDP"
                src_port = str(packet[UDP].sport)
                dst_port = str(packet[UDP].dport)
            elif ICMP in packet:
                proto = "ICMP"
                
        protocol_stats[proto] += 1
        
        pkt_info = {
            "time": float(packet.time),
            "proto": proto,
            "src": f"{src_ip}:{src_port}" if src_port else src_ip,
            "dst": f"{dst_ip}:{dst_port}" if dst_port else dst_ip,
            "length": len(packet)
        }
        
        packet_buffer.appendleft(pkt_info)
        
        if global_logger_ref and global_logger_ref.sql_enabled:
            from app.database import db_manager
            try:
                db_manager.insert_packet(pkt_info)
            except Exception:
                pass
        
        # Security Analysis (Port Scan detection etc.)
        if main_loop and global_logger_ref:
            security_manager.analyze_packet(packet, global_logger_ref, main_loop)
            
    except Exception as e:
        pass

global_logger_ref = None

async def monitor_packets(logger: Logger):
    global main_loop, global_logger_ref
    main_loop = asyncio.get_running_loop()
    global_logger_ref = logger
    
    sniffer = AsyncSniffer(filter='not host 127.0.0.1', prn=packet_callback, store=False)
    sniffer.start()
    
    try:
        while True:
            payload = {
                "type": "packets",
                "data": {
                    "stats": protocol_stats,
                    "recent": list(packet_buffer)[:50]
                }
            }
            
            logger.log_data("packets", payload["data"])
            await manager.broadcast(payload)
            await asyncio.sleep(2)
            
    except asyncio.CancelledError:
        try:
            sniffer.stop()
        except Exception:
            pass
