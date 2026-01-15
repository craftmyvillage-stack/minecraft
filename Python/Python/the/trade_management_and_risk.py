"""
FILE: trade_management_and_risk.py
STRATEGY VERSION: v2.0
"""
import logging
from datetime import datetime
from the.state_manager import state_engine

logger = logging.getLogger("TradeManager")

class TradeManagementEngine:
    def __init__(self, event_logger):
        self.event_logger = event_logger
        self.version = "v2.0"

    def check_exits(self):
        state_engine.heartbeat("risk_engine", "Monitoring v2.0 Risk")
        state = state_engine.get_state()
        active_trades = state.get("active_trades", {})
        market_data = state.get("market_data", {})
        
        now = datetime.now()
        hour, minute = now.hour, now.minute
        
        # Global Time Exit (2:30 PM)
        if (hour == 14 and minute >= 30) or hour > 14:
            if active_trades:
                self.close_all_trades("STRATEGY_TIME_FORCE_EXIT")
            return

        for tid, trade in list(active_trades.items()):
            symbol = trade['symbol']
            if symbol not in market_data: continue
            
            ltp = market_data[symbol]['close']
            entry = trade['entry_price']
            qty = trade['quantity']
            direction = trade['direction']
            regime = trade.get('regime', 'TRENDING')
            atr = trade.get('atr', 0.001)
            
            # 1. SL Logic (Immediate on entry)
            sl_mult = 2.0 if regime == "TRENDING" else 1.2
            sl_dist = entry * atr * sl_mult
            initial_sl = entry - sl_dist if direction == "BUY" else entry + sl_dist
            
            # 2. TSL Logic (Activates after 0.5R)
            current_tsl = trade.get('trailing_sl')
            target_05r = entry + (sl_dist * 0.5) if direction == "BUY" else entry - (sl_dist * 0.5)
            
            tsl_status = "WAITING"
            if (direction == "BUY" and ltp >= target_05r) or (direction == "SELL" and ltp <= target_05r):
                tsl_status = "ACTIVE"
                calculated_tsl = ltp - sl_dist if direction == "BUY" else ltp + sl_dist
                if current_tsl is None:
                    current_tsl = calculated_tsl
                elif direction == "BUY":
                    current_tsl = max(current_tsl, calculated_tsl)
                else:
                    current_tsl = min(current_tsl, calculated_tsl)
                
                if current_tsl != trade.get('trailing_sl'):
                    trade['trailing_sl'] = current_tsl
                    state_engine.register_trade(tid, trade)

            # 3. MPL Logic (3R Target)
            mpl_target = entry + (sl_dist * 3.0) if direction == "BUY" else entry - (sl_dist * 3.0)
            
            # 4. Exit Controller Selection (Only one dominant)
            active_rule = "INITIAL_SL"
            exit_price_trigger = initial_sl
            
            if tsl_status == "ACTIVE":
                active_rule = "TRAILING_SL"
                exit_price_trigger = current_tsl
            
            # Check if MPL is hit (dominant if reached)
            mpl_hit = (direction == "BUY" and ltp >= mpl_target) or (direction == "SELL" and ltp <= mpl_target)
            sl_tsl_hit = (direction == "BUY" and ltp <= exit_price_trigger) or (direction == "SELL" and ltp >= exit_price_trigger)
            
            decision = "HOLD"
            if mpl_hit:
                active_rule = "MAX_PROFIT_LOCK"
                decision = "EXIT"
            elif sl_tsl_hit:
                decision = "EXIT"

            # MANDATORY LOGGING
            exit_engine_log = (
                f"EXIT_ENGINE: Price={ltp:.2f} | SL={initial_sl:.2f} | "
                f"TSL={current_tsl if current_tsl else 0:.2f} ({tsl_status}) | "
                f"MPL={mpl_target:.2f} | ActiveRule={active_rule} | Decision={decision}"
            )
            logger.info(exit_engine_log)
            self.event_logger.log_system_event("INFO", "RiskEngine", exit_engine_log)

            # Update trade state for UI
            trade['active_rule'] = active_rule
            trade['mpl_target'] = mpl_target
            trade['tsl_status'] = tsl_status
            state_engine.register_trade(tid, trade)

            if decision == "EXIT":
                self.close_trade(tid, ltp, (ltp - entry) * qty if direction == "BUY" else (entry - ltp) * qty, active_rule)

            # Partial Profit Booking (1.5R)
            if not trade.get('partial_done', False):
                target_15r = entry + (sl_dist * 1.5) if direction == "BUY" else entry - (sl_dist * 1.5)
                hit_15r = (direction == "BUY" and ltp >= target_15r) or (direction == "SELL" and ltp <= target_15r)
                if hit_15r:
                    self.partial_exit(tid, trade, ltp, 0.5)

    def partial_exit(self, trade_id, trade, price, pct):
        exit_qty = int(trade['quantity'] * pct)
        if exit_qty < 1: return
        
        pnl = (price - trade['entry_price']) * exit_qty if trade['direction'] == "BUY" else (trade['entry_price'] - price) * exit_qty
        
        state = state_engine.get_state()
        new_trade = trade.copy()
        new_trade['quantity'] -= exit_qty
        new_trade['partial_done'] = True
        
        state_engine.register_trade(trade_id, new_trade)
        state_engine.update_pnl(pnl)
        
        msg = f"PARTIAL EXIT (50%): Booked ₹{pnl:.2f} profit on {trade['symbol']} at {price:.2f}. Runner active."
        self.event_logger.log_system_event("INFO", "RiskEngine", msg)

    def close_trade(self, trade_id, exit_price, pnl, reason):
        trade = state_engine.get_state()["active_trades"].get(trade_id)
        if not trade: return
        
        state_engine.close_trade(trade_id)
        state_engine.update_pnl(pnl)
        
        # Log to DB as well
        self.event_logger.log_trade_exit(trade_id, exit_price, pnl, datetime.now().isoformat())
        
        msg = f"CLOSED: {trade['symbol']} at {exit_price:.2f} (EXIT: {reason}). PnL: ₹{pnl:.2f}"
        self.event_logger.log_system_event("INFO", "RiskEngine", msg)
        
        # Update thinking for dashboard
        state_engine.update_thinking({"trade_decision_reason": f"Exit triggered: {reason} on {trade['symbol']}"})

    def close_all_trades(self, reason):
        active_trades = state_engine.get_state().get("active_trades", {})
        market_data = state_engine.get_state().get("market_data", {})
        for tid, trade in list(active_trades.items()):
            ltp = market_data.get(trade['symbol'], {}).get('close', trade['entry_price'])
            pnl = (ltp - trade['entry_price']) * trade['quantity'] if trade['direction'] == "BUY" else (trade['entry_price'] - ltp) * trade['quantity']
            self.close_trade(tid, ltp, pnl, reason)
