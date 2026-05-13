import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
import logging

class ARIMAModel:
    def __init__(self, order=(5, 1, 0)):
        self.order = order
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def forecast(self, data, steps=30):
        """
        Generates forecast using ARIMA model.
        data: Series or list of price data
        steps: Number of days to forecast
        """
        self.logger.info(f"Generating {steps}-day ARIMA forecast...")
        try:
            # Fit model
            model = ARIMA(data, order=self.order)
            model_fit = model.fit()
            
            # Forecast
            forecast_results = model_fit.get_forecast(steps=steps)
            forecast_mean = forecast_results.predicted_mean
            confidence_intervals = forecast_results.conf_int()
            
            # Prepare results dataframe
            forecast_dates = pd.date_range(start=data.index[-1] + pd.Timedelta(days=1), periods=steps)
            forecast_df = pd.DataFrame({
                'date': forecast_dates.strftime('%Y-%m-%d'),
                'predicted_price': forecast_mean.values,
                'lower_bound': confidence_intervals.iloc[:, 0].values,
                'upper_bound': confidence_intervals.iloc[:, 1].values
            })
            
            return forecast_df
        except Exception as e:
            self.logger.error(f"ARIMA forecast error: {e}")
            return None
