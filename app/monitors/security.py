import time
import asyncio
from collections import defaultdict
from app.websocket_manager import manager
from app.logger import Logger

class SecurityMonitor:
    def __init__(self):
        # Known suspicious ports
        self.suspicious_ports = {
            4444: "Metasploit Default / Reverse Shell",
            6667: "IRC Botnet C2",
            1337: "Elite / Common Malware",
            31337: "Back Orifice",
            # Add more as needed
        }
        
        # Port scan tracking: ip -> { timestamp: set(ports) }
        self.port_scans = defaultdict(lambda: {"time": time.time(), "ports": set()})
        self.SCAN_TIME_WINDOW = 2.0 # seconds
        self.SCAN_PORT_THRESHOLD = 15 # ports in window
        
        # Bandwidth anomaly tracking
        # pid -> { avg: 0, count: 0, last_alert: 0 }
        self.process_bw_stats = defaultdict(lambda: {"avg": 0.0, "count": 0, "last_alert": 0})
        self.whitelisted_apps = set() # Application names
        self.SPIKE_THRESHOLD_MULTIPLIER = 5.0 # 500%
        self.SPIKE_MIN_BPS = 1024 * 1024 # 1 MB/s minimum to care

    async def _send_alert(self, logger: Logger, level: str, title: str, message: str, app_name: str = None):
        payload = {
            "type": "alert",
            "data": {
                "level": level,
                "title": title,
                "message": message,
                "app_name": app_name,
                "timestamp": time.time()
            }
        }
        logger.log_data("security_alert", payload["data"])
        await manager.broadcast(payload)

    def analyze_packet(self, packet, logger: Logger, loop):
        """Called for every packet by Scapy (Advanced Mode)"""
        try:
            from scapy.all import IP, TCP
            if packet.haslayer(IP) and packet.haslayer(TCP):
                src_ip = packet[IP].src
                dst_port = packet[TCP].dport
                flags = packet[TCP].flags
                
                # Simple SYN scan detection
                if flags == "S":
                    tracker = self.port_scans[src_ip]
                    current_time = time.time()
                    
                    if current_time - tracker["time"] > self.SCAN_TIME_WINDOW:
                        tracker["ports"].clear()
                        tracker["time"] = current_time
                    
                    tracker["ports"].add(dst_port)
                    
                    if len(tracker["ports"]) > self.SCAN_PORT_THRESHOLD:
                        # Alert
                        tracker["ports"].clear() # Reset to prevent spam
                        asyncio.run_coroutine_threadsafe(
                            self._send_alert(logger, "high", "Port Taraması (Port Scan)", f"{src_ip} adresi çok sayıda porta istek yapıyor!"),
                            loop
                        )
        except Exception:
            pass

    async def check_suspicious_ports(self, connections, logger: Logger):
        """Called periodically with active connections (Basic Mode)"""
        for conn in connections:
            rport = None
            if isinstance(conn['raddr'], str) and ':' in conn['raddr']:
                try:
                    rport = int(conn['raddr'].split(':')[-1])
                except:
                    pass
            
            if rport in self.suspicious_ports:
                app = conn.get('process_name', 'Bilinmeyen')
                msg = f"{app} uygulaması şüpheli bir porta ({rport} - {self.suspicious_ports[rport]}) bağlandı!"
                await self._send_alert(logger, "high", "Şüpheli Bağlantı", msg)

    async def detect_bandwidth_spike(self, pid: int, process_name: str, current_bps: float, logger: Logger):
        """Called periodically per process (Basic Mode)"""
        if process_name in self.whitelisted_apps:
            return

        stats = self.process_bw_stats[pid]
        current_time = time.time()
        
        # Don't alert more than once per 30 seconds per PID
        if current_time - stats["last_alert"] < 30:
            return
            
        if stats["count"] > 10: # Need baseline
            avg = stats["avg"]
            if current_bps > self.SPIKE_MIN_BPS and current_bps > (avg * self.SPIKE_THRESHOLD_MULTIPLIER):
                # Spike detected!
                mbps = current_bps / (1024*1024)
                msg = f"{process_name} (PID: {pid}) uygulamasının ağ kullanımında devasa bir artış tespit edildi: {mbps:.2f} MB/s"
                await self._send_alert(logger, "medium", "Anormal Veri Transferi", msg, app_name=process_name)
                stats["last_alert"] = current_time
        
        # Update running average
        stats["avg"] = (stats["avg"] * stats["count"] + current_bps) / (stats["count"] + 1)
        stats["count"] += 1

security_manager = SecurityMonitor()
