import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging

class DataCollector:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def fetch_historical_data(self, ticker, period="max", interval="1d"):
        """
        Fetches historical data from Yahoo Finance.
        """
        self.logger.info(f"Fetching historical data for {ticker}...")
        try:
            data = yf.download(ticker, period=period, interval=interval)
            if data.empty:
                self.logger.warning(f"No data fetched for {ticker} from Yahoo Finance.")
                return None
            
            # Clean column names
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            
            data.columns = [col.lower().replace(' ', '_') for col in data.columns]
            self.logger.info(f"Successfully fetched {len(data)} records for {ticker}.")
            return data
        except Exception as e:
            self.logger.error(f"Error fetching data for {ticker}: {e}")
            return None

    def fetch_latest_data(self, ticker, days=7):
        """
        Fetches the latest data for updating records.
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        return yf.download(ticker, start=start_date, end=end_date)
