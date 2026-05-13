import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class SentimentAnalyzer:
    def __init__(self):
        pass

    def get_sentiment_data(self, dates):
        """
        Generates mock sentiment data for the given dates.
        In a real scenario, this would involve NLP on news/social media.
        """
        sentiment_scores = []
        labels = ['Bullish', 'Neutral', 'Bearish']
        sources = ['Twitter', 'Reddit', 'News', 'Telegram']
        
        for date in dates:
            # Generate a score between -1 and 1
            score = np.random.uniform(-1, 1)
            
            if score > 0.2:
                label = 'Bullish'
            elif score < -0.2:
                label = 'Bearish'
            else:
                label = 'Neutral'
                
            sentiment_scores.append({
                'date': date.strftime('%Y-%m-%d') if isinstance(date, datetime) else str(date)[:10],
                'score': round(score, 2),
                'sentiment_label': label,
                'source': np.random.choice(sources)
            })
            
        return pd.DataFrame(sentiment_scores).set_index('date')

    def aggregate_sentiment(self, df):
        """
        Calculates overall sentiment metrics.
        """
        avg_score = df['score'].mean()
        label_counts = df['sentiment_label'].value_counts(normalize=True).to_dict()
        
        return {
            'average_sentiment_score': float(avg_score),
            'sentiment_distribution': label_counts
        }
