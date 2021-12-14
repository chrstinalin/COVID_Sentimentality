"""
Functions to use the program.
"""
from tweet_data import retrieve_new_tweets
from emotion_data import total_emotions
from tweet_data import to_datetime
from datetime import timedelta
from datetime import datetime
import plotly_data as pd
import covid_data as cd


def graph_date_range(start: str, end: str) -> None:
    """ Creates a graph from the inputted range.

    Preconditions:
        - start and end are in format YYYY-MM-DD.
        - to_datetime('2020-01-01') <= to_datetime(start) < to_datetime(end) < datetime.today()

    """
    pd.draw_input_graph(to_datetime(start), to_datetime(end))


def graph_csv() -> None:
    """ Creates a graph from the data in csv.
    """
    pd.draw_saved_graph()


def update(n: int, start: str) -> None:
    """ Updates OWID COVID-19 data and generates a new twitter_data.csv and tweet_emotional_index.csv
    over n number of days starting from start_date.
    Recommend attempting graph_csv() before attempting this function.

        Preconditions:
        - start is in format YYYY-MM-DD.
        - to_datetime('2020-01-01') <= to_datetime(start) <
          to_datetime(start) + timedelta(days=n) < datetime.today()
    """
    cd.update_processed_covid_data(cd.get_covid_data(), cd.process_data())
    tweets = retrieve_new_tweets(n, to_datetime(start), True)
    total_emotions(tweets, True)
