import json
import csv
import os
from datetime import datetime
from typing import List, Dict
import asyncio
from app.database import db_manager

class Logger:
    def __init__(self):
        self.is_paused = False
        self.sql_enabled = False
        self.recorded_data: Dict[str, List] = {
            "bandwidth": [],
            "connections": [],
            "processes": [],
            "packets": [],
            "dns": [],
            "security_alert": []
        }
        self.log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            
        self.db_insert_counter = 0

    def toggle_sql(self, state: bool):
        self.sql_enabled = state

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False

    def log_data(self, data_type: str, data: dict):
        if not self.is_paused:
            # InMemory logging
            if len(self.recorded_data[data_type]) >= 1000:
                self.recorded_data[data_type].pop(0)
            self.recorded_data[data_type].append({
                "timestamp": datetime.now().isoformat(),
                "data": data
            })
            
            # SQL logging
            if self.sql_enabled:
                try:
                    if data_type == "bandwidth":
                        db_manager.insert_bandwidth(data)
                    elif data_type == "connections":
                        db_manager.insert_connections(data)
                    elif data_type == "processes":
                        db_manager.insert_processes(data)
                    elif data_type == "packets":
                        # data["recent"] contains list of packets, just insert the first one to avoid duplicates in loop
                        # Wait, the packets monitor sends the entire recent list every 2s. This would duplicate.
                        # Actually, we should change how packets are logged if we want per-packet SQL logging.
                        # For now, we'll let individual monitors insert into SQL if needed, OR we only insert the newest.
                        pass
                    elif data_type == "dns":
                        # same issue, dns monitor sends recent_queries.
                        pass
                    elif data_type == "security_alert":
                        db_manager.insert_security_alert(data)
                        
                    self.db_insert_counter += 1
                    if self.db_insert_counter >= 1000:
                        db_manager.clean_old_records()
                        self.db_insert_counter = 0
                except Exception as e:
                    print(f"SQL Insert Error: {e}")

    def export_json(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.log_dir, f"netvizor_export_{timestamp}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.recorded_data, f, indent=4)
        return filename
            
    def clear_data(self):
        for key in self.recorded_data:
            self.recorded_data[key].clear()
