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
    <html>
      <head>
        <title>Trading Bot</title>
        <style>
          body {
            background:#0f172a;
            color:#e5e7eb;
            font-family: Arial, sans-serif;
            display:flex;
            justify-content:center;
            align-items:center;
            height:100vh;
          }
          .card {
            background:#020617;
            padding:30px 40px;
            border-radius:12px;
            box-shadow:0 0 20px rgba(0,0,0,0.5);
            text-align:center;
          }
          h1 { color:#22c55e; }
          p { margin-top:10px; color:#94a3b8; }
        </style>
      </head>
      <body>
        <div class="card">
          <h1>🚀 Trading Bot Running</h1>
          <p>Your bot is live and scanning the market.</p>
          <p>Status: <b>ACTIVE</b></p>
        </div>
      </body>
    </html>
    """
