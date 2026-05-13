import sqlite3
import pandas as pd
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="data/crypto_analysis.db"):
        self.db_path = db_path
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Historical Prices Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historical_prices (
                symbol TEXT,
                date TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                adj_close REAL,
                volume INTEGER,
                PRIMARY KEY (symbol, date)
            )
        ''')

        # Technical Indicators Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS technical_indicators (
                symbol TEXT,
                date TEXT,
                sma_20 REAL,
                sma_50 REAL,
                sma_200 REAL,
                rsi_14 REAL,
                macd REAL,
                macd_signal REAL,
                bb_upper REAL,
                bb_lower REAL,
                PRIMARY KEY (symbol, date),
                FOREIGN KEY (symbol, date) REFERENCES historical_prices (symbol, date)
            )
        ''')

        # Forecasts Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS forecasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                date TEXT,
                model_name TEXT,
                predicted_price REAL,
                lower_bound REAL,
                upper_bound REAL,
                created_at TEXT
            )
        ''')

        # Sentiment Data Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sentiment_data (
                symbol TEXT,
                date TEXT,
                score REAL,
                sentiment_label TEXT,
                source TEXT,
                PRIMARY KEY (symbol, date)
            )
        ''')

        # Project Stats Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                symbol TEXT,
                key TEXT,
                value REAL,
                updated_at TEXT,
                PRIMARY KEY (symbol, key)
            )
        ''')

        conn.commit()
        conn.close()

    def save_historical_data(self, df, symbol):
        conn = self.get_connection()
        # Clear existing data for this symbol
        conn.execute("DELETE FROM historical_prices WHERE symbol = ?", (symbol,))
        df = df.copy()
        df['symbol'] = symbol
        # Filter for expected columns
        cols = ['symbol', 'open', 'high', 'low', 'close', 'adj_close', 'volume']
        df = df[[c for c in cols if c in df.columns]]
        df.to_sql('historical_prices', conn, if_exists='append', index=True, index_label='date')
        conn.commit()
        conn.close()

    def save_indicators(self, df, symbol):
        conn = self.get_connection()
        # Clear existing data for this symbol
        conn.execute("DELETE FROM technical_indicators WHERE symbol = ?", (symbol,))
        df = df.copy()
        df['symbol'] = symbol
        # Filter for expected columns
        cols = ['symbol', 'sma_20', 'sma_50', 'sma_200', 'rsi_14', 'macd', 'macd_signal', 'bb_upper', 'bb_lower']
        df = df[[c for c in cols if c in df.columns]]
        df.to_sql('technical_indicators', conn, if_exists='append', index=True, index_label='date')
        conn.commit()
        conn.close()

    def save_forecast(self, df, model_name, symbol):
        conn = self.get_connection()
        df['model_name'] = model_name
        df['symbol'] = symbol
        df['created_at'] = datetime.now().isoformat()
        # Drop existing forecasts for this model/symbol before saving new ones
        conn.execute("DELETE FROM forecasts WHERE model_name = ? AND symbol = ?", (model_name, symbol))
        df.to_sql('forecasts', conn, if_exists='append', index=False)
        conn.commit()
        conn.close()

    def save_sentiment(self, df, symbol):
        conn = self.get_connection()
        # Clear existing data for this symbol
        conn.execute("DELETE FROM sentiment_data WHERE symbol = ?", (symbol,))
        df = df.copy()
        df['symbol'] = symbol
        # Filter for expected columns
        cols = ['symbol', 'score', 'sentiment_label', 'source']
        df = df[[c for c in cols if c in df.columns]]
        df.to_sql('sentiment_data', conn, if_exists='append', index=True, index_label='date')
        conn.commit()
        conn.close()

    def update_stat(self, key, value, symbol):
        conn = self.get_connection()
        conn.execute('''
            INSERT OR REPLACE INTO statistics (symbol, key, value, updated_at)
            VALUES (?, ?, ?, ?)
        ''', (symbol, key, value, datetime.now().isoformat()))
        conn.commit()
        conn.close()

    def get_historical_data(self, symbol, limit=None):
        conn = self.get_connection()
        query = "SELECT * FROM historical_prices WHERE symbol = ? ORDER BY date DESC"
        if limit:
            query += f" LIMIT {limit}"
        df = pd.read_sql_query(query, conn, params=(symbol,))
        conn.close()
        return df

    def get_forecasts(self, symbol, model_name=None):
        conn = self.get_connection()
        query = "SELECT * FROM forecasts WHERE symbol = ?"
        params = [symbol]
        if model_name:
            query += " AND model_name = ?"
            params.append(model_name)
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df

    def get_indicators(self, symbol, limit=None):
        conn = self.get_connection()
        query = "SELECT * FROM technical_indicators WHERE symbol = ? ORDER BY date DESC"
        if limit:
            query += f" LIMIT {limit}"
        df = pd.read_sql_query(query, conn, params=(symbol,))
        conn.close()
        return df

    def get_all_stats(self, symbol):
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM statistics WHERE symbol = ?", conn, params=(symbol,))
        conn.close()
        return dict(zip(df['key'], df['value']))
