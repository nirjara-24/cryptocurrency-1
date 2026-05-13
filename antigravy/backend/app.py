from flask import Flask, jsonify, request
from flask_cors import CORS
from database import DatabaseManager
import pandas as pd
from datetime import datetime

from data_collector import DataCollector
from preprocessor import Preprocessor
from sentiment_analyzer import SentimentAnalyzer
from models.arima_model import ARIMAModel

app = Flask(__name__)
CORS(app)
db = DatabaseManager()
collector = DataCollector()
preprocessor = Preprocessor()
sentiment_analyzer = SentimentAnalyzer()

@app.route('/api/search', methods=['GET'])
def search_ticker():
    symbol = request.args.get('symbol', '').upper()
    if not symbol:
        return jsonify({"error": "No symbol provided"}), 400
    
    # Check if we already have data
    existing = db.get_historical_data(symbol, limit=1)
    if not existing.empty:
        return jsonify({"status": "exists", "symbol": symbol})

    # Otherwise, initialize the new ticker
    try:
        # 1. Fetch data
        df = collector.fetch_historical_data(symbol, period="1y") # Fetch 1y for speed
        if df is None:
            return jsonify({"error": f"Could not find data for {symbol}"}), 404
        
        # 2. Process
        df_with_indicators = preprocessor.calculate_indicators(df)
        db.save_historical_data(df, symbol)
        db.save_indicators(df_with_indicators, symbol)
        
        # 3. Stats
        stats = preprocessor.get_summary_stats(df)
        for key, value in stats.items():
            db.update_stat(key, value, symbol)
            
        # 4. Fast Forecast (ARIMA only for on-demand search)
        arima = ARIMAModel()
        arima_forecast = arima.forecast(df['close'])
        if arima_forecast is not None:
            db.save_forecast(arima_forecast, 'ARIMA', symbol)
            
        # 5. Sentiment (Mock)
        sentiment_df = sentiment_analyzer.get_sentiment_data(df.tail(30).index)
        db.save_sentiment(sentiment_df, symbol)

        return jsonify({"status": "initialized", "symbol": symbol})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/historical-data', methods=['GET'])
def get_historical_data():
    symbol = request.args.get('symbol', default='BTC-USD')
    days = request.args.get('days', default=365, type=int)
    df = db.get_historical_data(symbol, limit=days)
    data = df.iloc[::-1].to_dict(orient='records')
    return jsonify(data)

@app.route('/api/indicators', methods=['GET'])
def get_indicators():
    symbol = request.args.get('symbol', default='BTC-USD')
    days = request.args.get('days', default=100, type=int)
    df = db.get_indicators(symbol, limit=days)
    data = df.iloc[::-1].to_dict(orient='records')
    return jsonify(data)

@app.route('/api/forecasts', methods=['GET'])
def get_forecasts():
    symbol = request.args.get('symbol', default='BTC-USD')
    model_name = request.args.get('model', default=None)
    df = db.get_forecasts(symbol, model_name=model_name)
    data = df.to_dict(orient='records')
    return jsonify(data)

@app.route('/api/sentiment', methods=['GET'])
def get_sentiment():
    symbol = request.args.get('symbol', default='BTC-USD')
    days = request.args.get('days', default=30, type=int)
    conn = db.get_connection()
    query = f"SELECT * FROM sentiment_data WHERE symbol = ? ORDER BY date DESC LIMIT {days}"
    df = pd.read_sql_query(query, conn, params=(symbol,))
    conn.close()
    data = df.iloc[::-1].to_dict(orient='records')
    return jsonify(data)

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    symbol = request.args.get('symbol', default='BTC-USD')
    stats = db.get_all_stats(symbol)
    return jsonify(stats)

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({"status": "running", "timestamp": datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
