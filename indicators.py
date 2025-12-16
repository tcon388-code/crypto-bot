import pandas as pd
import pandas_ta as ta
from config import RSI_PERIOD

def process_kline_data(kline_data):
    """
    Convert MEXC kline data to DataFrame.
    MEXC Kline structure from 'contract/kline/{symbol}' usually is:
    {
        "time": [t1, t2, ...],
        "open": [o1, o2, ...],
        ...
    }
    """
    if not kline_data:
        return pd.DataFrame()
    
    try:
        # Check if it's the structure with keys for lists
        if isinstance(kline_data, dict) and 'time' in kline_data:
            df = pd.DataFrame(kline_data)
            # Rename columns if needed or standardise
            # Expected cols: time, open, high, low, close, vol, amount
            # specific processing
            df['close'] = pd.to_numeric(df['close'])
            # df['time'] = pd.to_datetime(df['time'], unit='s') # Optional, usually keeping unix is fine for internal
            return df
        
        # If it's list of lists (Common for APIs)
        if isinstance(kline_data, list):
             # MEXC Futures V1 Kline usually: [time, open, high, low, close, vol, ...]
             # But let's be safe and assume:
             # If elements are lists:
             if len(kline_data) > 0 and isinstance(kline_data[0], list):
                 # Columns based on common standard: time, open, high, low, close...
                 # We mainly need 'close' for RSI.
                 # Let's support the standard O-H-L-C format
                 cols = ['time', 'open', 'high', 'low', 'close', 'vol']
                 # Retrieve first 6 columns, ignoring extra stats if any
                 df = pd.DataFrame([x[:6] for x in kline_data], columns=cols)
                 df['close'] = pd.to_numeric(df['close'])
                 return df
             
        return pd.DataFrame()
    except Exception as e:
        print(f"Error processing kline data: {e}")
        return pd.DataFrame()

def calculate_rsi(df, period=RSI_PERIOD):
    """
    Calculate RSI for the DataFrame using pandas_ta.
    Assumes 'close' column exists.
    """
    if df.empty or 'close' not in df.columns:
        return None
        
    try:
        # Calculate RSI
        rsi_series = df.ta.rsi(length=period)
        if rsi_series is None or rsi_series.empty:
            return None
        
        # Return the last RSI value (current candle)
        # Note: The last candle might be incomplete. 
        # Usually for alerts we look at the last completed or current real-time.
        # User requested "Price: ... RSI: ...". 
        # We will return the last calculated value.
        return round(rsi_series.iloc[-1], 2)
    except Exception as e:
        print(f"Error calculating RSI: {e}")
        return None
