import logging
import time
import json
import os
from datetime import datetime
from config import TIMEFRAMES, RSI_OVERBOUGHT, RSI_EXTREME, RSI_RESET, MIN_TIMEFRAME_MATCH
from mexc_api import MexcAPI
from indicators import process_kline_data, calculate_rsi

logger = logging.getLogger(__name__)

class BotScanner:
    def __init__(self, telegram_bot):
        self.api = MexcAPI()
        self.telegram = telegram_bot
        self.alerted_coins = {} # {symbol: {'timestamp': time, 'values': {}}}

    def save_results(self, results):
        """
        Save scan results to public/results.json safely (atomic write)
        """
        try:
            output_data = {
                "updated_at": datetime.now().strftime("%H:%M:%S %d/%m/%Y"),
                "data": results
            }
            
            # Ensure folder exists
            os.makedirs("public", exist_ok=True)
            
            temp_file = "public/results.json.tmp"
            target_file = "public/results.json"
            
            with open(temp_file, "w") as f:
                json.dump(output_data, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            
            os.replace(temp_file, target_file)
                
            logger.info("Results saved to public/results.json")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")

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
        
        # Determine Signal for Web View
        signal = "Wait"
        if overbought_count >= MIN_TIMEFRAME_MATCH:
             if extreme_count > 0:
                 signal = "EXTREME SHORT"
             else:
                 signal = "SHORT"
        
        # Prepare Result Dict
        result_entry = {
            "symbol": symbol,
            "rsi_15m": rsi_results.get('15m', 0),
            "rsi_1h": rsi_results.get('1h', 0),
            "signal": signal,
            "price": current_price
        }

        # 3. Check Alert Condition (Telegram)
        if signal != "Wait" and symbol not in self.alerted_coins: # Only alert if not already alerted (simple check)
             # Note: Actual spam logic is slightly more complex above (reset logic), 
             # but here we rely on the implementation plan which focused on web integration.
             # Re-integrating specific alert logic:
             
             is_extreme = (extreme_count > 0)
             msg = self.format_alert_message(symbol, current_price, rsi_results, is_extreme)
             
             logger.info(f"Sending alert for {symbol}")
             self.telegram.send_message(msg)
             
             # Mark as alerted
             self.alerted_coins[symbol] = {
                 'timestamp': time.time(),
                 'rsi': rsi_results
             }

        return result_entry

    def scan_market(self):
        """
        Main loop to scan all pairs.
        """
        symbols = self.api.get_all_futures_symbols()
        logger.info(f"Starting scan for {len(symbols)} pairs...")
        
        scan_results = []
        
        for symbol in symbols:
            try:
                result = self.process_pair(symbol)
                if result:
                    scan_results.append(result)
                
                # Rate limit prevention (though purely public API is lenient, good practice)
                time.sleep(0.1) 
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
        
        # Sort results by urgency (e.g. signal != Wait first)
        scan_results.sort(key=lambda x: 0 if x['signal'] == 'Wait' else 1, reverse=True)
        
        self.save_results(scan_results)
        logger.info("Scan completed.")
