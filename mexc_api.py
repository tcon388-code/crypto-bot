import requests
import logging
from config import MEXC_FUTURES_BASE_URL, TIMEFRAMES

logger = logging.getLogger(__name__)

class MexcAPI:
    def __init__(self):
        self.base_url = MEXC_FUTURES_BASE_URL

    def get_all_futures_symbols(self):
        """
        Fetch all available futures contracts.
        Returns a list of symbols (e.g., ['BTC_USDT', 'ETH_USDT']).
        """
        try:
            url = f"{self.base_url}/api/v1/contract/detail"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data['success']:
                symbols = []
                for item in data['data']:
                    # Filter only enabled and USDT pairs if needed
                    # item['state'] == 0 usually means enabled
                    if item.get('state') == 0 and item['symbol'].endswith('_USDT'):
                        symbols.append(item['symbol'])
                return symbols
            else:
                logger.error(f"Failed to fetch symbols: {data}")
                return []
        except requests.RequestException as e:
            logger.error(f"Error fetching symbols: {e}")
            return []

    def get_kline(self, symbol, interval, limit=100):
        """
        Fetch kline (candle) data.
        
        Args:
            symbol (str): e.g., 'BTC_USDT'
            interval (str): 'Min1', 'Min5', ... (Use values from config.TIMEFRAMES)
            limit (int): Number of candles to fetch (Default: 100 for RSI calc)
            
        Returns:
            list: List of dicts or raw data. MEXC returns list of values.
            [time, open, low, high, close, vol, quantity]
        """
        try:
            # Endpoint: /api/v1/contract/kline/{symbol}
            # Query params: interval, limit
            # Note: The docs say path param is symbol.
            url = f"{self.base_url}/api/v1/contract/kline/{symbol}"
            headers = {'Accept': 'application/json'}
            params = {
                'interval': interval,
                'limit': limit
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if data['success']:
                # Data format: 
                # "data": { "time": [...], "open": [...], "close": [...], "high": [...], "low": [...] } 
                # OR is it a list of lists?
                # Based on recent experiences with MEXC API, it often returns specific structures.
                # Let's handle the structure.
                # Common MEXC Structure for kline public:
                # { "success": true, "code": 0, "data": { "time": [...], "high": [...], ... } }
                return data['data']
            else:
                logger.warning(f"Error fetching kline for {symbol} {interval}: {data}")
                return None
        except requests.RequestException as e:
            logger.error(f"Request error for {symbol} {interval}: {e}")
            return None
