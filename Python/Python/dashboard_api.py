import sys
import os
# Ensure the directory containing 'the' is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

"""
FILE: dashboard_api.py
STRATEGY VERSION: v2.0
"""
import sqlite3
from fastapi import FastAPI
from fastapi.responses import FileResponse
try:
    from the.state_manager import state_engine
    from the.event_logger import EventLogger
except ImportError:
    # Handle direct execution or alternative structures
    sys.path.append(os.path.join(BASE_DIR, ".."))
    from the.state_manager import state_engine
    from the.event_logger import EventLogger

app = FastAPI()
event_logger = EventLogger()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "trading_bot_audit.db")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))
    

@app.get("/health")
async def get_health():
    state = state_engine.get_state()
    return {"ready": True, "status": "SYSTEM READY - STRATEGY V2.0", "health_data": state["system_health"]}

@app.get("/status")
async def get_status():
    state = state_engine.get_state()
    # Mock performance v2
    perf = {"win_rate": 68.5, "total": 124, "avg_rr": "1:1.5", "drawdown": "2.1%"}
    
    return {
        "mode": state["system_mode"],
        "bot_state": state["bot_thinking"].get("current_state", "IDLE"),
        "market_status": state["bot_thinking"].get("market_status", "CLOSED"),
        "data_source": state["bot_thinking"].get("data_source", "SIMULATED"),
        "last_update": state["bot_thinking"].get("last_update", "--:--:--"),
        "latency": state["bot_thinking"].get("data_latency", "--ms"),
        "daily_pnl": state["daily_loss"]["current"],
        "thinking": state["bot_thinking"],
        "performance": perf,
        "health": state["system_health"],
        "version": "v2.0"
    }

@app.get("/logs/recent")
async def get_recent_logs():
    return event_logger.get_recent_logs(15)

@app.get("/trades/active")
async def get_active_trades():
    return list(state_engine.get_state()["active_trades"].values())

DB_PATH = os.path.join(BASE_DIR, "trading_bot_audit.db")

@app.get("/trades/closed")
async def get_closed_trades():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trades ORDER BY exit_time DESC LIMIT 10")
        return [dict(r) for r in cursor.fetchall()]
    except:
        return []

@app.get("/audit/market_ticks")
async def get_market_ticks():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM market_data ORDER BY id DESC LIMIT 20")
            return [dict(row) for row in cursor.fetchall()]
    except Exception: return []

@app.get("/audit/execution_traces")
async def get_execution_traces():
    try:
        import json
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM execution_traces ORDER BY id DESC LIMIT 10")
            rows = []
            for row in cursor.fetchall():
                d = dict(row)
                d['steps'] = json.loads(d['steps'])
                rows.append(d)
            return rows
    except Exception: return []

if __name__ == "__main__":
    import os
    import uvicorn
    # Replit requires port 5000 for webview
    port = 5000
    uvicorn.run(app, host="0.0.0.0", port=port)

