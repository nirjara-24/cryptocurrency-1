import pandas as pd
import numpy as np

class Preprocessor:
    @staticmethod
    def calculate_indicators(df):
        """
        Calculates technical indicators for the given dataframe.
        Expects a dataframe with a 'close' column.
        """
        df = df.copy()
        
        # Simple Moving Averages
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        df['sma_200'] = df['close'].rolling(window=200).mean()
        
        # Relative Strength Index (RSI)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi_14'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        
        # Bollinger Bands
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        df['bb_std'] = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * 2)
        df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * 2)
        
        # Drop temporary columns
        df.drop(['bb_middle', 'bb_std'], axis=1, inplace=True)
        
        return df

    @staticmethod
    def get_summary_stats(df):
        """
        Calculates summary statistics for the dashboard.
        """
        if len(df) < 2:
            return {
                'latest_price': float(df['close'].iloc[-1]) if not df.empty else 0.0,
                'change_24h': 0.0,
                'high_52w': 0.0,
                'low_52w': 0.0,
                'avg_volume': 0.0
            }
            
        latest_price = df['close'].iloc[-1]
        prev_price = df['close'].iloc[-2]
        change_24h = ((latest_price - prev_price) / prev_price) * 100
        
        # Determine window size based on available data
        high_low_window = min(len(df), 365)
        vol_window = min(len(df), 30)
        
        high_52w = df['high'].rolling(window=high_low_window).max().iloc[-1]
        low_52w = df['low'].rolling(window=high_low_window).min().iloc[-1]
        avg_volume = df['volume'].rolling(window=vol_window).mean().iloc[-1]
        
        return {
            'latest_price': float(latest_price),
            'change_24h': float(change_24h),
            'high_52w': float(high_52w),
            'low_52w': float(low_52w),
            'avg_volume': float(avg_volume)
        }
