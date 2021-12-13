"""
Code for retrieving and processing Tweets scraped from Twitter.
"""
from datetime import timedelta
from datetime import datetime
from ast import literal_eval
from twint import token
import backoff
import pandas
import twint


def to_twint(date: datetime) -> str:
    """Returns a datetime in Twitter format.

    >>> to_twint(datetime(2021, 1, 2, 23, 59))
    '2021-01-02'
    """
    return date.strftime('%Y-%m-%d')


def to_datetime(date: str) -> datetime: # CALLED TO FIND END_DATE.
    """Returns a date in Twitter format as datetime.

    >>> to_datetime('2021-01-02')
    datetime.datetime(2021, 1, 2, 23, 59)
    """
    if '23:59:00' not in date:
        date += ' 23:59:00'
    return datetime.strptime(date, '%Y-%m-%d %H:%M:%S')


@backoff.on_exception(
    backoff.expo,
    twint.token.RefreshTokenException,
    max_tries=20
)
def retrieve_day_tweets(date: datetime) -> tuple[datetime, list]:
    """Return a tuple with 20 COVID-related tweets from a given day, formatted as (date, tweets).
    if store is True, saves the raw data to a csv.
    """

    # Configuration
    twt = twint.Config()
    twt.Lang = 'en'
    twt.Limit = 20
    twt.Search = 'covid until:' + to_twint(date + timedelta(days=1)) + ' since:' + to_twint(date)

    # Raw Data List
    raw_tweets = []
    twt.Store_object = True
    twt.Store_object_tweets_list = raw_tweets

    # Run
    twint.run.Search(twt)

    # Reformat
    tweets = [tweet.tweet for tweet in raw_tweets]
    return (date, tweets)


@backoff.on_exception(
    backoff.expo,
    twint.token.RefreshTokenException,
    max_tries=10
)
def retrieve_new_tweets(n: int, start_date: datetime, save: bool) -> tuple[datetime, list[tuple[datetime, list]]]:
    """Returns n days' worth of tweets. Saves the results to a csv when save is True.
    Tuple maps the start of the week to (date, list of tweets).
    """
    current_date = start_date
    week_so_far = []

    for _ in range(n):
        day_tweets = (current_date, [])
        while day_tweets[1] == []:
            day_tweets = retrieve_day_tweets(current_date)
        week_so_far.append(day_tweets)
        current_date += timedelta(days=1)

    if save:
        save_to_raw_data(week_so_far)

    return (start_date, week_so_far)


def save_to_raw_data(data: list[tuple[datetime, list]]) -> None:
    """ Saves retrieved tweets to twitter_data.csv.
    """
    # noinspection PyTypeChecker
    pandas.DataFrame(data, columns=['date', 'tweets']).to_csv('twitter_data.csv', index=False)


def pull_from_raw_data() -> list[tuple[datetime, list]]:
    """ Returns the data in twitter_data.csv.
    """
    data = pandas.read_csv('twitter_data.csv').values.tolist()
    return [(to_datetime(pair[0]), literal_eval(pair[1])) for pair in data]
