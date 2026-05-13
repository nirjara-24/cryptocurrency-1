import pandas as pd
from prophet import Prophet
import logging

class ProphetModel:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def forecast(self, data, steps=30):
        """
        Generates forecast using Facebook Prophet.
        data: DataFrame with index as date and 'close' column
        steps: Number of days to forecast
        """
        self.logger.info(f"Generating {steps}-day Prophet forecast...")
        try:
            # Prepare data for Prophet (requires 'ds' and 'y' columns)
            df_prophet = data[['close']].reset_index()
            df_prophet.columns = ['ds', 'y']
            # Ensure ds is datetime
            df_prophet['ds'] = pd.to_datetime(df_prophet['ds']).dt.tz_localize(None)
            
            # Fit model
            model = Prophet(daily_seasonality=True, weekly_seasonality=True, yearly_seasonality=True)
            model.fit(df_prophet)
            
            # Forecast
            future = model.make_future_dataframe(periods=steps)
            forecast = model.predict(future)
            
            # Extract last 'steps' days
            forecast_result = forecast.tail(steps)[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
            forecast_df = pd.DataFrame({
                'date': forecast_result['ds'].dt.strftime('%Y-%m-%d'),
                'predicted_price': forecast_result['yhat'].values,
                'lower_bound': forecast_result['yhat_lower'].values,
                'upper_bound': forecast_result['yhat_upper'].values
            })
            
            return forecast_df
        except Exception as e:
            self.logger.error(f"Prophet forecast error: {e}")
            return None
