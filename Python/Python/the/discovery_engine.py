import random
import time
import logging
from datetime import datetime
from the.state_manager import state_engine

logger = logging.getLogger("DiscoveryEngine")

class DiscoveryEngine:
    def __init__(self):
        self.universe = [
            "NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", # Indices
            "RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY", # Top Stocks (Configurable)
            "BHARTIARTL", "SBIN", "LICI", "ITC", "HUL",
            "RELIANCE", "AXISBANK", "KOTAKBANK", "LT", "BAJFINANCE"
        ]
        self.last_ticks = {s: {"price": random.uniform(500, 25000), "volume": 1000, "time": time.time()} for s in self.universe}
        self.focus_list = []
        self.max_focus = 4
        self.energy_threshold = 65

    def stage_0_radar(self):
        """Lightweight Scanner: No indicators, no history."""
        hot_opportunities = []
        
        for symbol in self.universe:
            # Simulate a new tick for scanning
            current_price = self.last_ticks[symbol]["price"] * (1 + random.uniform(-0.001, 0.001))
            current_vol = self.last_ticks[symbol]["volume"] + random.randint(10, 500)
            now = time.time()
            
            # Velocity: % move
            dt = now - self.last_ticks[symbol]["time"]
            velocity = abs(current_price - self.last_ticks[symbol]["price"]) / self.last_ticks[symbol]["price"] * 100
            
            # Volume Burst Ratio (Simulated)
            vol_burst = random.uniform(0.5, 2.5) 
            
            # Energy Score Calculation (Velocity + VolBurst)
            energy_score = (velocity * 500) + (vol_burst * 20)
            energy_score = min(100, max(0, int(energy_score)))
            
            reason = "Idle"
            if energy_score >= self.energy_threshold:
                reason = "Momentum Spike" if velocity > 0.05 else "Volume Burst"
                hot_opportunities.append({
                    "symbol": symbol,
                    "energy_score": energy_score,
                    "reason": reason,
                    "velocity": velocity,
                    "vol_burst": vol_burst,
                    "price": current_price,
                    "volume": current_vol
                })
            
            # Update last tick
            self.last_ticks[symbol] = {"price": current_price, "volume": current_vol, "time": now}
            
        return hot_opportunities

    def stage_1_focus(self, hot_opps):
        """Maintain TOP 2-4 HOT instruments."""
        # Sort by energy score
        hot_opps.sort(key=lambda x: x['energy_score'], reverse=True)
        
        new_focus = [opp['symbol'] for opp in hot_opps[:self.max_focus]]
        
        # Log transition
        if set(new_focus) != set(self.focus_list):
            logger.info(f"FOCUS_ENGINE | Transition: {self.focus_list} -> {new_focus}")
            
        self.focus_list = new_focus
        state_engine.update_thinking({"focus_list": self.focus_list, "hot_count": len(hot_opps)})
        return self.focus_list

    def get_discovery_state(self):
        return {
            "focus_list": self.focus_list,
            "universe_size": len(self.universe)
        }
