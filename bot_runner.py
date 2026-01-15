import time
import logging
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from the.market_data_and_signal import MarketSignalEngine
from the.trade_execution_and_mode import ExecutionEngine
from the.trade_management_and_risk import TradeManagementEngine
from the.event_logger import EventLogger

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
            signals = signal_engine.scan_market()

            for sig in signals:
                event_logger.log_signal(sig)
                execution_engine.execute_trade(sig)

            risk_engine.check_exits()
            time.sleep(2)

        except Exception as e:
            logger.error(f"Loop Error: {e}")
            time.sleep(5)
