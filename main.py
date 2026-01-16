from fastapi import FastAPI
from fastapi.responses import FileResponse
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

@app.get("/")
def root():
    return FileResponse("index.html")
