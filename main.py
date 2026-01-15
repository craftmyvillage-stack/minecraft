from fastapi import FastAPI
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
    return {"status": "Trading bot running 🚀"}


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BotOrchestrator")

def main_loop():
    logger.info("[SYSTEM READY] Paper trading live with TradingView data")
    
    event_logger = EventLogger()
    signal_engine = MarketSignalEngine()
    execution_engine = ExecutionEngine()
    risk_engine = TradeManagementEngine(event_logger)

    while True:
        try:
            # 1. Market Data & Signal Generation
            signals = signal_engine.scan_market()
            
            # 2. Trade Execution
            for sig in signals:
                event_logger.log_signal(sig)
                execution_engine.execute_trade(sig)

            # 3. Trade Management & Risk
            risk_engine.check_exits()
            
            time.sleep(2) # 2-second interval as per requirement
        except Exception as e:
            logger.error(f"Loop Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main_loop()
