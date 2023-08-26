import nltk
import logging
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer


# Setup logging
logging.basicConfig(level=logging.INFO)


class SentimentAnalyzer:
    NEGATIVE_THRESHOLD = -0.05
    POSITIVE_THRESHOLD = 0.05

    def __init__(self, df):
        if not isinstance(df, pd.DataFrame):
            raise ValueError("df should be a pandas DataFrame")

        self.df = df
        self.sid = SentimentIntensityAnalyzer()

        # try:
        #     nltk.download('vader_lexicon')
        # except Exception as e:
        #     logging.error(
        #         f"An error occurred while downloading the 'vader_lexicon'.")
        #     raise e

    def get_sentiment(self, score):
        """Determines sentiment category based on the score."""
        if score < self.NEGATIVE_THRESHOLD:
            return 'Negative'
        elif score > self.POSITIVE_THRESHOLD:
            return 'Positive'
        else:
            return 'Neutral'

    def analyze(self):
        """Performs sentiment analysis on the data."""
        if self.df is None:
            logging.error("No DataFrame provided to analyze.")
            return None

        try:
            self.df['scores'] = self.df['text'].apply(
                lambda text: self.sid.polarity_scores(text))
            self.df['compound'] = self.df['scores'].apply(
                lambda score_dict: score_dict['compound'])
            self.df['sentiment'] = self.df['compound'].apply(
                self.get_sentiment)
            return self.df
        except Exception as e:
            logging.error(f"An error occurred while analyzing sentiment.")
            raise e
