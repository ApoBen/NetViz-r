import asyncio
from collections import deque, Counter
from scapy.all import AsyncSniffer, DNSQR, DNSRR, IP
from app.websocket_manager import manager
from app.logger import Logger

dns_log = deque(maxlen=100)
domain_counter = Counter()

def dns_callback(packet):
    try:
        if packet.haslayer(DNSRR):
            # Check DNSRR first — response packets also contain DNSQR
            if packet.an:
                domain = packet[DNSRR].rrname.decode('utf-8', errors='replace').rstrip('.')
                rdata = str(packet[DNSRR].rdata)
                
                dns_log.appendleft({
                    "time": float(packet.time),
                    "domain": domain,
                    "type": "Response",
                    "data": rdata
                })
            
        elif packet.haslayer(DNSQR):
            query = packet[DNSQR].qname.decode('utf-8', errors='replace').rstrip('.')
            qtype = packet[DNSQR].qtype
            
            src_ip = packet[IP].src if IP in packet else "Unknown"
            
            # Record the query
            dns_log.appendleft({
                "time": float(packet.time),
                "domain": query,
                "type": "Query",
                "src": src_ip
            })
            domain_counter[query] += 1
    except Exception:
        pass

async def monitor_dns(logger: Logger):
    # Only capture UDP port 53 (DNS)
    sniffer = AsyncSniffer(filter="udp port 53", prn=dns_callback, store=False)
    sniffer.start()
    
    try:
        while True:
            # Get top 15 domains
            top_domains = [{"domain": k, "count": v} for k, v in domain_counter.most_common(15)]
            
            payload = {
                "type": "dns",
                "data": {
                    "top_domains": top_domains,
                    "recent_queries": list(dns_log)[:30]
                }
            }
            
            logger.log_data("dns", payload["data"])
            await manager.broadcast(payload)
            await asyncio.sleep(3) # Update every 3 seconds
            
    except asyncio.CancelledError:
        try:
            sniffer.stop()
        except Exception:
            pass
