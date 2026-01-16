from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import threading
from bot_runner import main_loop

app = FastAPI()
bot_thread = None

@app.on_event("startup")
def start_bot():
    global bot_thread
    if bot_thread is None:
        bot_thread = threading.Thread(target=main_loop, daemon=True)
        bot_thread.start()

@app.get("/", response_class=HTMLResponse)
def root():
    return """
<!DOCTYPE html>
<html>
<head>
  <title>CYBER-TRADER</title>
  <style>
    body {
      margin:0;
      font-family: Arial, sans-serif;
      background:#020617;
      color:#e5e7eb;
      display:flex;
    }
    .sidebar {
      width:220px;
      background:#020617;
      border-right:1px solid #0f172a;
      padding:20px;
    }
    .logo {
      color:#22c55e;
      font-size:22px;
      font-weight:bold;
    }
    .menu div {
      margin:15px 0;
      color:#94a3b8;
      cursor:pointer;
    }
    .menu .active {
      color:#22c55e;
      font-weight:bold;
    }
    .main {
      flex:1;
      padding:30px;
    }
    .banner {
      background:#ef4444;
      color:white;
      padding:12px;
      text-align:center;
      font-weight:bold;
      border-radius:6px;
      margin-bottom:25px;
    }
    .cards {
      display:grid;
      grid-template-columns: repeat(4, 1fr);
      gap:15px;
      margin-bottom:20px;
    }
    .card {
      background:#020617;
      border:1px solid #0f172a;
      border-radius:10px;
      padding:20px;
      box-shadow:0 0 10px rgba(0,0,0,0.4);
    }
    .green { color:#22c55e; }
    .box {
      margin-top:15px;
    }
    .tags span {
      background:#052e2b;
      color:#22c55e;
      padding:6px 10px;
      border-radius:6px;
      margin-right:8px;
      display:inline-block;
      margin-top:6px;
    }
  </style>
</head>
<body>
  <div class="sidebar">
    <div class="logo">CYBER-TRADER</div>
    <small>SYSTEM ARCHITECT v2.0</small>
    <div class="menu" style="margin-top:30px;">
      <div class="active">OVERVIEW</div>
      <div>LIVE MARKET FEED</div>
      <div>STRATEGY & REGIME</div>
      <div>TRADES</div>
      <div>LOGS & DIAGNOSTICS</div>
    </div>
  </div>

  <div class="main">
    <div class="banner">SIMULATION MODE – NO REAL TRADES</div>

    <h2>System Overview</h2>
    <div class="cards">
      <div class="card">
        <small>BOT MODE</small>
        <h3 class="green">PAPER</h3>
      </div>
      <div class="card">
        <small>BOT STATE</small>
        <h3>ANALYZING</h3>
      </div>
      <div class="card">
        <small>MARKET STATUS</small>
        <h3 class="green">Market OPEN</h3>
      </div>
      <div class="card">
        <small>DAILY P&L</small>
        <h3 class="green">₹0.00</h3>
      </div>
    </div>

    <div class="cards">
      <div class="card">
        <h3>Current Reasoning</h3>
        <p class="green">Initializing...</p>
      </div>
      <div class="card">
        <h3>Market Discovery (Focus List)</h3>
        <div class="tags">
          <span>NIFTY</span>
          <span>LICI</span>
          <span>INFY</span>
          <span>AXISBANK</span>
        </div>
      </div>
    </div>

    <div class="cards">
      <div class="card">
        <h3>Confidence & Regime</h3>
        <p>REGIME: <b>TRENDING</b></p>
        <p>CONFIDENCE SCORE: <span class="green">0%</span></p>
      </div>
    </div>
  </div>
</body>
</html>
"""
