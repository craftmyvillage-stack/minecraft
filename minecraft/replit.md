# Replit.md - Trading Bot System

## Overview

This is an intraday paper trading bot system designed for simulating trades on Indian indices (NIFTY, BANKNIFTY) and crypto (BTCUSDT). The system operates entirely in paper trading mode using simulated TradingView-style market data.

**Core Purpose:** Simulate trading strategies with confidence-weighted signal generation, execute paper trades, manage risk with adaptive stop-losses and time-based exits, and display real-time performance on a web dashboard.

**Key Characteristics:**
- Paper trading only (no real money, no broker APIs)
- Simulated market data (no external API keys needed)
- Self-contained system with file-based state persistence
- FastAPI-powered dashboard for monitoring
- Strategy v2.0 with weighted confidence engine

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Pipeline Architecture

The system follows a continuous loop architecture with four distinct stages:

```
Market Data → Signal Generation → Trade Execution → Risk Management
     ↓              ↓                   ↓                  ↓
  (OHLC)        (BUY/SELL)          (Paper Fill)      (SL/Time Exit)
```

**Main Orchestrator** (`main.py`):
- Runs an infinite loop with 2-second intervals
- Coordinates all engines in sequence
- Handles errors gracefully with automatic recovery

### Module Responsibilities

| File | Purpose |
|------|---------|
| `main.py` | Central orchestrator - runs the trading loop |
| `the/market_data_and_signal.py` | Generates simulated OHLC data and trading signals with v2.0 confidence engine |
| `the/trade_execution_and_mode.py` | Executes paper trades based on signals with confidence filtering |
| `the/trade_management_and_risk.py` | Monitors positions, handles adaptive stop-losses and time-based exits |
| `the/state_manager.py` | Single source of truth for all system state (JSON file-based) |
| `the/event_logger.py` | Audit logging with SQLite persistence |
| `dashboard_api.py` | FastAPI server for web dashboard |
| `index.html` | Trading terminal UI (inline CSS only) |

### State Management Design

**File-based persistence** using `bot_state.json`:
- Stores system mode, active trades, market data, and bot thinking state
- Uses file locking (fcntl) for safe concurrent access
- Auto-creates with defaults if missing
- Resets daily loss tracking on date change

**Key State Properties:**
- `system_mode`: Always "PAPER" (no live trading)
- `active_trades`: Current open positions (max 2)
- `bot_thinking`: Real-time decision explanation for dashboard
- `system_health`: Heartbeat status for all engines

### Signal Generation (v2.0 Strategy)

**Weighted Confidence Engine:**
- Trend strength: 35%
- Volume alignment: 20%
- RSI alignment: 20%
- Volatility (ATR): 15%
- Time-of-day score: 10%

**Entry Requirements:**
- Minimum confidence threshold: 65%
- Candle confirmation (close above/below previous high/low)
- Volume spike ≥ 1.2x average

### Risk Management

**Adaptive Stop-Loss:**
- Trending regime: 2x ATR distance
- Choppy regime: 1.2x ATR distance

**Exit Conditions:**
- Stop-loss hit
- Partial profit at 1R (1.5x SL distance)
- Time-based exit at 2:30 PM
- Daily loss limit breach (₹150)

### Web Dashboard

**Endpoints:**
- `GET /` - Serves index.html
- `GET /health` - System health status
- `GET /status` - Current mode, P&L, thinking state

**Dashboard Features:**
- Real-time confidence breakdown
- Bot thinking/reasoning display
- Active trades table
- System health indicators

## External Dependencies

### Python Packages
| Package | Purpose |
|---------|---------|
| `fastapi` | Web framework for dashboard API |
| `uvicorn` | ASGI server to run FastAPI |

### Data Storage
| Component | Technology | Purpose |
|-----------|------------|---------|
| State persistence | JSON file (`bot_state.json`) | Active trades, system state |
| Audit logging | SQLite (`trading_bot_audit.db`) | Signals, trades, system logs |

### External APIs
**None required.** The system uses internally simulated market data that mimics TradingView-style OHLC candles. No broker connections, no API keys, no external data feeds.

### File Structure Notes
- All core modules live in `Python/the/` directory
- The `the/` package requires `__init__.py` (present but empty)
- State and database files are created in `Python/` root directory
- Imports use `from the.module_name import ...` pattern