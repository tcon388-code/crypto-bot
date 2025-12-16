import time
import logging
from bot_logic import BotScanner
from telegram_sender import TelegramBot
from dotenv import load_dotenv

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Main")

def main():
    logger.info("Starting MEXC Futures RSI Scanner Bot...")
    
    # 1. Init Telegram
    telegram = TelegramBot()
    
    # 2. Init Scanner
    scanner = BotScanner(telegram)
    
    # 3. Loop
    while True:
        try:
            logger.info("Starting new scan cycle...")
            start_time = time.time()
            scanner.scan_market()
            elapsed = time.time() - start_time
            
            logger.info(f"Scan cycle finished in {elapsed:.2f}s. Sleeping for 60 seconds...")
            time.sleep(60) 
            
        except KeyboardInterrupt:
            logger.info("Bot stopped by user.")
            break
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
            time.sleep(10) # Wait before retry

if __name__ == "__main__":
    main()
