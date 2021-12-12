"""
Code for retrieving and processing Tweets scraped from Twitter.
"""
from datetime import timedelta
from datetime import datetime
from os import remove
from os import path
import pandas
import twint
import time


def datetime_to_twint(date: datetime) -> str:
    """Returns a datetime in Twitter format.

    >>> datetime_to_twint(datetime(2021, 1, 2, 23, 59))
    '2021-01-02'
    """
    return date.strftime('%Y-%m-%d')


def twint_to_datetime(date: str) -> datetime: # CALLED TO FIND END_DATE.
    """Returns a date in Twitter format as datetime.

    >>> twint_to_datetime('2021-01-02')
    datetime.datetime(2021, 1, 2, 23, 59)
    """
    return datetime.strptime(date + ' 23:59:00', '%Y-%m-%d %H:%M:%S')


def retrieve_day_tweets(date: datetime, store: bool) -> tuple[datetime, list]:
    """Return a tuple with 20 COVID-related tweets from a given day, formatted as (date, tweets).
    if store is True, saves the raw data to a csv.
    """

    # Configuration
    twt = twint.Config()
    twt.Lang = 'en'
    twt.Limit = 20
    twt.Search = 'covid until:' + datetime_to_twint(date + timedelta(days=1)) + ' since:' + datetime_to_twint(date)

    # Store to Raw Data CSV if overwrite is True
    if store:
        twt.Store_csv = True
        twt.Output = 'raw_twitter_data_sample.csv'

    # Raw Data List
    raw_tweets = []
    twt.Store_object = True
    twt.Store_object_tweets_list = raw_tweets

    # Run
    twint.run.Search(twt)

    # Reformat
    tweets = [tweet.tweet for tweet in raw_tweets]
    return (date, tweets)


def retrieve_new_tweets(n: int, end_date: datetime, overwrite: bool) -> tuple[datetime, list[tuple]]:
    """Returns n days' worth of tweets. Saves the results to a csv.
    Tuple maps the end of the week to (date, list of tweets).
    """
    current_date = end_date
    week_so_far = []

    if overwrite:
        file = 'raw_twitter_data_sample.csv'
        if path.exists(file):
            remove(file)

    for _ in range(n):
        day_tweets = (current_date, [])
        while day_tweets[1] == []:
            day_tweets = retrieve_day_tweets(current_date, overwrite)
            time.sleep(10)
        week_so_far.append(day_tweets)
        current_date -= timedelta(days=1)

    return (end_date, week_so_far)


# WARNING: Because of Twitter limits, TWINT is not always able to fetch new tweets without token expiry.
# May need to wait, or use previously-fetched data (below).


def pull_from_raw_data() -> tuple[datetime, list[tuple]]:
    """ Returns the data in raw_twitter_data_sample.csv.
    """
    data = pandas.read_csv('raw_twitter_data_sample.csv')
    temp_dict = {}

    for _, row in data.iterrows():
        date = twint_to_datetime(row[3])
        if date not in temp_dict:
            temp_dict[date] = []
        temp_dict[date].append(row[10])

    lst = [(key, temp_dict[key]) for key in temp_dict]
    return (lst[0][0], lst)
