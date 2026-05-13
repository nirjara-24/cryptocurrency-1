import sys
import os
import pandas as pd
from datetime import datetime
import logging

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from database import DatabaseManager
from data_collector import DataCollector
from preprocessor import Preprocessor
from sentiment_analyzer import SentimentAnalyzer
from models.arima_model import ARIMAModel
from models.prophet_model import ProphetModel
from models.lstm_model import LSTMModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize(symbols=None):
    if symbols is None:
        symbols = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD", 
                   "ADA-USD", "DOGE-USD", "DOT-USD", "MATIC-USD", "LINK-USD"]
    
    logger.info(f"Starting project initialization for {len(symbols)} assets...")
    
    db = DatabaseManager()
    collector = DataCollector()
    preprocessor = Preprocessor()
    sentiment_analyzer = SentimentAnalyzer()
    
    for idx, symbol in enumerate(symbols):
        logger.info(f"\n--- [{idx+1}/{len(symbols)}] Initializing {symbol} ---")
        try:
            # 1. Fetch data
            df = collector.fetch_historical_data(symbol)
            if df is None:
                logger.error(f"Failed to fetch historical data for {symbol}. Skipping.")
                continue
            
            # 2. Preprocess & Save Indicators
            df_with_indicators = preprocessor.calculate_indicators(df)
            db.save_historical_data(df, symbol)
            db.save_indicators(df_with_indicators, symbol)
            
            # 3. Calculate Stats
            stats = preprocessor.get_summary_stats(df)
            for key, value in stats.items():
                db.update_stat(key, value, symbol)
            
            # 4. Generate & Save Sentiment
            sentiment_df = sentiment_analyzer.get_sentiment_data(df.tail(90).index)
            db.save_sentiment(sentiment_df, symbol)
            
            # 5. Train & Forecast (Check if already exists to save time)
            existing_forecasts = db.get_forecasts(symbol)
            models_to_train = []
            if 'ARIMA' not in existing_forecasts['model_name'].values: models_to_train.append('ARIMA')
            if 'Prophet' not in existing_forecasts['model_name'].values: models_to_train.append('Prophet')
            if 'LSTM' not in existing_forecasts['model_name'].values: models_to_train.append('LSTM')

            if not models_to_train:
                logger.info(f"Models for {symbol} already exist. Skipping training.")
                continue

            # ARIMA (Fast)
            if 'ARIMA' in models_to_train:
                arima = ARIMAModel()
                arima_forecast = arima.forecast(df['close'])
                if arima_forecast is not None:
                    db.save_forecast(arima_forecast, 'ARIMA', symbol)
                
            # Prophet (Medium)
            if 'Prophet' in models_to_train:
                prophet = ProphetModel()
                prophet_forecast = prophet.forecast(df)
                if prophet_forecast is not None:
                    db.save_forecast(prophet_forecast, 'Prophet', symbol)
                
            # LSTM (Slow - using very small tail for faster training during init)
            if 'LSTM' in models_to_train:
                lstm = LSTMModel()
                # Use only last 200 days for training during initialization
                lstm_forecast = lstm.forecast(df['close'].tail(200))
                if lstm_forecast is not None:
                    db.save_forecast(lstm_forecast, 'LSTM', symbol)
                
            logger.info(f"Successfully initialized {symbol}")
        except Exception as e:
            logger.error(f"Error initializing {symbol}: {e}")
            continue
        
    logger.info("\nInitialization complete for all assets!")

if __name__ == "__main__":
    initialize()
