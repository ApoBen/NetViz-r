import sqlite3
import os
import json
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="netvizor.db"):
        self.db_path = db_path
        self._init_db()

    def _get_conn(self):
        # We use check_same_thread=False since asyncio/threads might share connection,
        # but in Python SQLite it's safer to open connection per thread/task, 
        # or use a lock. For simple inserts, we can open and close.
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _init_db(self):
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # Bandwidth table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bandwidth (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                upload_speed REAL,
                download_speed REAL
            )
        ''')
        
        # Connections table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS connections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                laddr TEXT,
                raddr TEXT,
                status TEXT,
                pid INTEGER
            )
        ''')

        # Processes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                pid INTEGER,
                name TEXT,
                username TEXT,
                upload_speed REAL,
                download_speed REAL,
                total_upload REAL,
                total_download REAL
            )
        ''')

        # Packets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS packets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                proto TEXT,
                src TEXT,
                dst TEXT,
                length INTEGER
            )
        ''')

        # DNS table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                type TEXT,
                domain TEXT,
                src TEXT,
                data TEXT
            )
        ''')

        # Security alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                level TEXT,
                title TEXT,
                message TEXT,
                source_ip TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def insert_bandwidth(self, data):
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("INSERT INTO bandwidth (timestamp, upload_speed, download_speed) VALUES (?, ?, ?)",
                  (datetime.now().isoformat(), data.get("upload", 0), data.get("download", 0)))
        conn.commit()
        conn.close()

    def insert_connections(self, data):
        conn = self._get_conn()
        c = conn.cursor()
        timestamp = datetime.now().isoformat()
        
        # Extract the list from the dictionary payload
        conn_list = data.get("connections", []) if isinstance(data, dict) else data
        
        for conn_item in conn_list:
            if isinstance(conn_item, dict):
                c.execute("INSERT INTO connections (timestamp, laddr, raddr, status, pid) VALUES (?, ?, ?, ?, ?)",
                          (timestamp, conn_item.get("laddr"), conn_item.get("raddr"), conn_item.get("status"), conn_item.get("pid")))
        conn.commit()
        conn.close()

    def insert_processes(self, data):
        conn = self._get_conn()
        c = conn.cursor()
        timestamp = datetime.now().isoformat()
        
        # Extract the list from the dictionary payload
        proc_list = data.get("processes", []) if isinstance(data, dict) else data
        
        for proc in proc_list:
            if isinstance(proc, dict):
                c.execute('''INSERT INTO processes 
                            (timestamp, pid, name, username, upload_speed, download_speed, total_upload, total_download) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                          (timestamp, proc.get("pid"), proc.get("name"), proc.get("username"),
                           proc.get("upload_speed", 0), proc.get("download_speed", 0),
                           proc.get("total_upload", 0), proc.get("total_download", 0)))
        conn.commit()
        conn.close()

    def insert_packet(self, pkt):
        # pkt comes from packet_buffer inside packets.py
        conn = self._get_conn()
        c = conn.cursor()
        # time is stored in pkt["time"]
        dt = datetime.fromtimestamp(pkt.get("time", datetime.now().timestamp())).isoformat()
        c.execute("INSERT INTO packets (timestamp, proto, src, dst, length) VALUES (?, ?, ?, ?, ?)",
                  (dt, pkt.get("proto"), pkt.get("src"), pkt.get("dst"), pkt.get("length")))
        conn.commit()
        conn.close()

    def insert_dns(self, query):
        conn = self._get_conn()
        c = conn.cursor()
        dt = datetime.fromtimestamp(query.get("time", datetime.now().timestamp())).isoformat()
        c.execute("INSERT INTO dns (timestamp, type, domain, src, data) VALUES (?, ?, ?, ?, ?)",
                  (dt, query.get("type"), query.get("domain"), query.get("src", ""), query.get("data", "")))
        conn.commit()
        conn.close()

    def insert_security_alert(self, alert):
        conn = self._get_conn()
        c = conn.cursor()
        dt = datetime.now().isoformat()
        c.execute("INSERT INTO security_alerts (timestamp, level, title, message, source_ip) VALUES (?, ?, ?, ?, ?)",
                  (dt, alert.get("level"), alert.get("title"), alert.get("message"), alert.get("source_ip", "")))
        conn.commit()
        conn.close()

    def clean_old_records(self, max_rows=10000):
        # Optional: prevent DB from growing forever by keeping only recent N rows.
        # This can be called periodically.
        conn = self._get_conn()
        c = conn.cursor()
        tables = ["bandwidth", "connections", "processes", "packets", "dns", "security_alerts"]
        for t in tables:
            c.execute(f"DELETE FROM {t} WHERE id NOT IN (SELECT id FROM {t} ORDER BY id DESC LIMIT {max_rows})")
        conn.commit()
        conn.close()

db_manager = DatabaseManager()
