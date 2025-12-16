import telebot
import logging
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.enabled = False
        if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
            self.bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
            self.chat_id = TELEGRAM_CHAT_ID
            self.enabled = True
            logging.info("Telegram Bot configured.")
        else:
            logging.warning("Telegram Bot Token or Chat ID missing. Alerts will only be logged.")

    def send_message(self, message):
        """
        Send a message to the configured Telegram chat.
        """
        if not self.enabled:
            logger.info(f"[SIMULATION] Telegram Alert:\n{message}")
            return

        try:
            self.bot.send_message(self.chat_id, message, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
