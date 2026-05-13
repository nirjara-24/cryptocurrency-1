import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import logging

# Deep learning specific imports - handled within the method to avoid crashes if unavailable
class LSTMModel:
    def __init__(self, window_size=60):
        self.window_size = window_size
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def forecast(self, data, steps=30):
        """
        Generates forecast using LSTM neural network.
        data: Series or list of price data
        steps: Number of days to forecast
        """
        self.logger.info(f"Generating {steps}-day LSTM forecast...")
        try:
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import LSTM, Dense, Dropout
            
            # Prepare data
            # Flatten to numpy array if it's a pandas object
            values = data.values.reshape(-1, 1)
            scaler = MinMaxScaler(feature_range=(0, 1))
            scaled_data = scaler.fit_transform(values)
            
            # Create training set for simple demonstration (normally pre-trained)
            x_train = []
            y_train = []
            for i in range(self.window_size, len(scaled_data)):
                x_train.append(scaled_data[i-self.window_size:i, 0])
                y_train.append(scaled_data[i, 0])
            
            x_train, y_train = np.array(x_train), np.array(y_train)
            x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
            
            # Build Model (Simplified for demo)
            model = Sequential()
            model.add(LSTM(units=50, return_sequences=True, input_shape=(x_train.shape[1], 1)))
            model.add(Dropout(0.2))
            model.add(LSTM(units=50))
            model.add(Dropout(0.2))
            model.add(Dense(units=1))
            
            model.compile(optimizer='adam', loss='mean_squared_error')
            # Train for a few epochs for demonstration
            model.fit(x_train, y_train, epochs=2, batch_size=32, verbose=0)
            
            # Forecast
            last_window = scaled_data[-self.window_size:]
            current_batch = last_window.reshape((1, self.window_size, 1))
            
            future_predictions = []
            for i in range(steps):
                pred = model.predict(current_batch, verbose=0)[0]
                future_predictions.append(pred)
                # Append prediction and slide window
                current_batch = np.append(current_batch[:, 1:, :], [[pred]], axis=1)
            
            # Inverse transform
            predicted_prices = scaler.inverse_transform(future_predictions)
            
            # Prepare results dataframe
            forecast_dates = pd.date_range(start=data.index[-1] + pd.Timedelta(days=1), periods=steps)
            forecast_df = pd.DataFrame({
                'date': forecast_dates.strftime('%Y-%m-%d'),
                'predicted_price': predicted_prices.flatten(),
                # Simulating bounds for LSTM
                'lower_bound': predicted_prices.flatten() * 0.95,
                'upper_bound': predicted_prices.flatten() * 1.05
            })
            
            return forecast_df
        except Exception as e:
            self.logger.error(f"LSTM forecast error: {e}")
            # Fallback to a simple trend if TF/LSTM fails
            self.logger.info("Falling back to trend-based forecast for LSTM.")
            return self._fallback_forecast(data, steps)

    def _fallback_forecast(self, data, steps):
        last_price = data.iloc[-1]
        returns = data.pct_change().dropna().tail(30).mean()
        forecast_dates = pd.date_range(start=data.index[-1] + pd.Timedelta(days=1), periods=steps)
        predicted = [last_price * (1 + returns)**i for i in range(1, steps + 1)]
        return pd.DataFrame({
            'date': forecast_dates.strftime('%Y-%m-%d'),
            'predicted_price': predicted,
            'lower_bound': [p * 0.9 for p in predicted],
            'upper_bound': [p * 1.1 for p in predicted]
        })
