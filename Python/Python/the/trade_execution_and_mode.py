"""
FILE: trade_execution_and_mode.py
STRATEGY VERSION: v2.0
"""
import time
from datetime import datetime
from the.state_manager import state_engine

class ExecutionEngine:
    def __init__(self):
        self.max_capital = 1000.0
        self.min_confidence = 0.65
        self.version = "v2.0"
        self._ensure_trace_table()

    def _ensure_trace_table(self):
        import sqlite3
        try:
            with sqlite3.connect("trading_bot_audit.db") as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS execution_traces (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        trace_id TEXT,
                        timestamp TEXT,
                        symbol TEXT,
                        signal_type TEXT,
                        confidence REAL,
                        steps TEXT
                    )
                """)
        except Exception: pass

    def _log_trace(self, trace):
        import sqlite3
        import json
        try:
            with sqlite3.connect("trading_bot_audit.db") as conn:
                conn.execute("""
                    INSERT INTO execution_traces (trace_id, timestamp, symbol, signal_type, confidence, steps)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (trace['trace_id'], trace['timestamp'], trace['symbol'], trace['signal_type'], trace['confidence'], json.dumps(trace['steps'])))
        except Exception: pass

    def execute_trade(self, signal):
        state_engine.heartbeat("execution_engine", "v2.0 Ready")
        state = state_engine.get_state()
        data_mode = state.get("data_mode", "SIMULATION")
        system_mode = state.get("system_mode", "PAPER")

        # TRACE START: MANDATORY DECISION PIPELINE LOGGING
        trace_id = f"TRACE_{int(time.time())}_{signal['symbol']}"
        decision_trace = {
            "trace_id": trace_id,
            "timestamp": datetime.now().isoformat(),
            "symbol": signal['symbol'],
            "signal_type": signal['signal_type'],
            "confidence": signal['confidence'],
            "steps": []
        }

        # Step 1: Signal Generation Check
        decision_trace["steps"].append("SIGNAL_GENERATED")

        # HARD-BLOCK: Ensure system is ONLY in PAPER mode
        if system_mode != "PAPER":
            reason = "CRITICAL: Bot is hard-coded for PAPER mode only. Execution blocked."
            decision_trace["steps"].append(f"EXECUTION_BLOCKED | Reason: {reason}")
            self._log_trace(decision_trace)
            state_engine.update_thinking({
                "trade_rejection_reason": reason,
                "strategy_trace": "SYSTEM_MODE_LOCK -> BLOCKED"
            })
            return None
        
        # DATA MODE ENFORCEMENT: Strictly block if not REAL data
        if data_mode != "REAL":
            reason = f"BLOCK: DATA_MODE={data_mode}. Trade execution requires REAL TradingView data."
            decision_trace["steps"].append("RISK_CHECK_FAILED")
            decision_trace["steps"].append(f"EXECUTION_BLOCKED | Reason: SIMULATION")
            self._log_trace(decision_trace)
            state_engine.update_thinking({
                "trade_rejection_reason": reason,
                "strategy_trace": f"SIGNAL {signal['signal_type']} -> RISK_CHECK -> BLOCKED (NON-REAL DATA)"
            })
            return None

        decision_trace["steps"].append("RISK_CHECK_PASSED")

        # 2. Confidence Filter
        if signal['confidence'] < self.min_confidence:
            reason = f"Confidence {signal['confidence']*100:.0f}% < {self.min_confidence*100:.0f}%"
            decision_trace["steps"].append(f"EXECUTION_BLOCKED | Reason: CONFIDENCE")
            self._log_trace(decision_trace)
            state_engine.update_thinking({"trade_rejection_reason": reason})
            return None

        # 3. Active Limit
        if len(state['active_trades']) >= 2:
            reason = "Max active trades reached"
            decision_trace["steps"].append(f"EXECUTION_BLOCKED | Reason: LIMIT")
            self._log_trace(decision_trace)
            state_engine.update_thinking({"trade_rejection_reason": reason})
            return None

        decision_trace["steps"].append("EXECUTION_ALLOWED")
        self._log_trace(decision_trace)
        
        ltp = signal['price']
        qty = max(1, int(self.max_capital / ltp))
        
        trade_id = f"V2_{int(time.time())}_{signal['symbol']}"
        trade_data = {
            "trade_id": trade_id,
            "symbol": signal['symbol'],
            "direction": signal['signal_type'],
            "quantity": qty,
            "entry_price": ltp,
            "timestamp": datetime.now().isoformat(),
            "regime": signal['regime'],
            "atr": signal['atr'],
            "version": self.version,
            "partial_done": False,
            "mode": state.get("system_mode", "PAPER"),
            "signal_id": f"SIG_{int(time.time())}",
            "indicators_at_entry": signal.get('indicators', {}),
            "entry_reason": f"Signal generated with {signal['confidence']*100:.0f}% confidence in {signal['regime']} regime"
        }
        
        state_engine.register_trade(trade_id, trade_data)
        
        # Register with Event Logger for DB
        from the.event_logger import EventLogger
        event_logger = EventLogger()
        event_logger.log_trade_entry(trade_data)

        state_engine.update_thinking({"trade_decision_reason": f"V2 Entry: {signal['signal_type']} based on {signal['regime']} regime."})
        return trade_data
