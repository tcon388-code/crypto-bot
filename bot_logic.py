import logging
import time
from config import TIMEFRAMES, RSI_OVERBOUGHT, RSI_EXTREME, RSI_RESET, MIN_TIMEFRAME_MATCH
from mexc_api import MexcAPI
from indicators import process_kline_data, calculate_rsi

logger = logging.getLogger(__name__)

class BotScanner:
    def __init__(self, telegram_bot):
        self.api = MexcAPI()
        self.telegram = telegram_bot
        self.alerted_coins = {} # {symbol: {'timestamp': time, 'values': {}}}

    def get_rsi_status_emoji(self, rsi_value):
        if rsi_value > RSI_EXTREME:
            return "🔴" # Extreme
        elif rsi_value > RSI_OVERBOUGHT:
            return "🟡" # Overbought
        else:
            return "⚪" # Normal

    def format_alert_message(self, symbol, price, rsi_results, extreme_risk=False):
        """
        Format the Telegram message.
        """
        msg = f"🚨 *{symbol}* – Giá: `{price}`\n\n"
        msg += "📊 *RSI:*\n"
        
        # Sort timeframes for consistent display order
        # We can use the keys from config or a fixed order list
        display_order = ['1m', '5m', '15m', '30m', '1h', '4h', '1d']
        
        for tf in display_order:
            if tf in rsi_results:
                val = rsi_results[tf]
                emoji = self.get_rsi_status_emoji(val)
                msg += f"{tf} {emoji} `{val}`\n"
        
        msg += f"\n🔥 *OVERBOUGHT CONFIRMED* (≥{MIN_TIMEFRAME_MATCH} TFs)"
        
        if extreme_risk:
            msg += "\n\n☠️ *EXTREME OVERBOUGHT – HIGH SHORT RISK*"
            
        return msg

    def process_pair(self, symbol):
        """
        Process a single pair: fetch candles, calc RSI, check alerts.
        """
        rsi_results = {}
        overbought_count = 0
        extreme_count = 0
        
        current_price = 0
        
        # 1. Fetch data for all timeframes
        # Optimisation: Maybe fetch 1m first? If 1m is low, maybe skip others? 
        # But requirement says "at least 2 timeframes > 80". 
        # So we should probably check higher TFs too.
        
        for tf_name, tf_code in TIMEFRAMES.items():
            kline_data = self.api.get_kline(symbol, tf_code)
            if not kline_data:
                continue
                
            df = process_kline_data(kline_data)
            rsi = calculate_rsi(df)
            
            if rsi is not None:
                rsi_results[tf_name] = rsi
                # Capture current price from the lowest timeframe (e.g. 1m or 5m) or just last one
                if current_price == 0 and not df.empty:
                    current_price = df.iloc[-1]['close']
                
                if rsi > RSI_OVERBOUGHT:
                    overbought_count += 1
                if rsi > RSI_EXTREME:
                    extreme_count += 1
        
        # 2. Check Spam Control (Reset Logic)
        if symbol in self.alerted_coins:
            # Check if all RSI < RSI_RESET
            all_cool = True
            for rsi in rsi_results.values():
                if rsi >= RSI_RESET:
                    all_cool = False
                    break
            
            if all_cool:
                logger.info(f"{symbol} cooled down. Resetting alert status.")
                del self.alerted_coins[symbol]
            
            # If already alerted and not cooled down, suppress new alert
            return

        # 3. Check Alert Condition
        if overbought_count >= MIN_TIMEFRAME_MATCH:
            # Trigger Alert
            is_extreme = (extreme_count > 0) # Requirement: "If RSI > 90 -> add warning"
            
            msg = self.format_alert_message(symbol, current_price, rsi_results, is_extreme)
            
            logger.info(f"Sending alert for {symbol}")
            self.telegram.send_message(msg)
            
            # Mark as alerted
            self.alerted_coins[symbol] = {
                'timestamp': time.time(),
                'rsi': rsi_results
            }

    def scan_market(self):
        """
        Main loop to scan all pairs.
        """
        symbols = self.api.get_all_futures_symbols()
        logger.info(f"Starting scan for {len(symbols)} pairs...")
        
        for symbol in symbols:
            try:
                self.process_pair(symbol)
                # Rate limit prevention (though purely public API is lenient, good practice)
                time.sleep(0.1) 
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
        
        logger.info("Scan completed.")
