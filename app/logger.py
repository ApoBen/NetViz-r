import json
import csv
import os
from datetime import datetime
from typing import List, Dict

class Logger:
    def __init__(self):
        self.is_paused = False
        self.recorded_data: Dict[str, List] = {
            "bandwidth": [],
            "connections": [],
            "processes": [],
            "packets": [],
            "dns": []
        }
        self.log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False

    def log_data(self, data_type: str, data: dict):
        if not self.is_paused:
            # We don't want to grow indefinitely if running for days without exporting.
            # Keep only the last 1000 records per type in memory to prevent OOM.
            if len(self.recorded_data[data_type]) > 1000:
                self.recorded_data[data_type].pop(0)
            self.recorded_data[data_type].append({
                "timestamp": datetime.now().isoformat(),
                "data": data
            })

    def export_json(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.log_dir, f"netvizor_export_{timestamp}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.recorded_data, f, indent=4)
        return filename
            
    def clear_data(self):
        for key in self.recorded_data:
            self.recorded_data[key].clear()
