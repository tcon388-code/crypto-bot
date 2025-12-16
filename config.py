import os
from dotenv import load_dotenv

load_dotenv()

# MEXC Futures API Parameters
MEXC_FUTURES_BASE_URL = "https://contract.mexc.com"

# Telegram Settings
# User needs to create a .env file with TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Logic Parameters
RSI_PERIOD = 14
RSI_OVERBOUGHT = 80
RSI_EXTREME = 90
RSI_RESET = 75

# Timeframes to scan
# API interval mapping: 'Min1', 'Min5', 'Min15', 'Min30', 'Min60', 'Hour4', 'Day1'
TIMEFRAMES = {
    '1m': 'Min1',
    '5m': 'Min5',
    '15m': 'Min15',
    '30m': 'Min30',
    '1h': 'Min60',
    '4h': 'Hour4',
    '1d': 'Day1'
}

# Minimum timeframes required to trigger alert
MIN_TIMEFRAME_MATCH = 2

# Filter out coins with low volume? (Optional, set 0 to disable)
MIN_VOLUME_USDT = 100000 
