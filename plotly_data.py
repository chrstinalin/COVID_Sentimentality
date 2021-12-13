"""
Code for retrieving specific emotions from dictionary of emotions over a period of time and graphing
it with COVID data against time using plotly.
"""
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import emotion_data as ed
import tweet_data as td
import covid_data as cd
import datetime

emotions = ['anger', 'anticipation', 'disgust', 'fear', 'joy', 'negative', 'positive',
            'sadness', 'surprise', 'trust']
covid_data_types = list(cd.process_data().header)


def get_emotion(start_date: datetime, end_date: datetime) -> dict:
    """Given a start and end date, returns a dictionary mapping each day to its emotional index.
    """
    num_days = (end_date - start_date).days
    data = td.retrieve_new_tweets(num_days + 1, start_date, False)
    tweet_data = ed.total_emotions(data, False)
    return tweet_data


def get_emotion_by_day(tweet_data: dict, chosen_emotion: str) -> list:
    """ Retrieves a single emotion's data across several days.
    """
    emotion_by_day = []
    for date in tweet_data:
        emotion_by_day.append(tweet_data[date][chosen_emotion])
    return emotion_by_day


def get_emotion_from_file(chosen_emotion: str) -> (datetime, datetime, list):
    """ Retrieves a single emotion's data from tweet_emotional_index.csv
        and returns (start_date, end_date, data)
    """
    emotion_data = ed.pull_from_raw_data()
    emotion_by_day = []
    for date in emotion_data:
        emotion_by_day.append(emotion_data[date][chosen_emotion])

    start = td.to_datetime(min(emotion_data))
    end = td.to_datetime(max(emotion_data))

    return (start, end, emotion_by_day)


def get_desired_dates(start_date: datetime, end_date: datetime) -> list:
    """Return a set of dates in twint format from start_date to end_date.
    """
    desired_dates = []
    for n in range((end_date - start_date).days + 1):
        desired_dates.append(td.to_twint(start_date + datetime.timedelta(n)))
    return desired_dates


def get_covid_data(start_date: datetime, end_date: datetime, chosen_covid_data: str) -> list:
    """Returns a subset of COVID data given a start and end date.
    """
    covid_data = cd.process_data().set_index('header').to_dict()
    desired_dates = get_desired_dates(start_date, end_date)
    covid_data_by_day = []
    for date in desired_dates:
        covid_data_by_day.append(covid_data[date][chosen_covid_data])
    return covid_data_by_day


def draw_input_graph(start_date: datetime, end_date: datetime, chosen_emotion: str, chosen_covid_data: str):
    """Plots COVID and emotional data from start_date to end_date.
    """
    fig = make_subplots(specs=[[{'secondary_y': True}]])
    dates = get_desired_dates(start_date, end_date)
    covid_data = get_covid_data(start_date, end_date, chosen_covid_data)
    emotion_data = get_emotion_by_day(get_emotion(start_date, end_date), chosen_emotion)

    fig.add_trace(
        go.Scatter(
            x=dates,
            y=emotion_data,
            name=f'{chosen_emotion.capitalize()}',
            marker=dict(color='#1A70C7'),
            line=dict(width=6)
        ),
        secondary_y=True,
    )

    fig.add_trace(
        go.Bar(
            x=dates,
            y=covid_data,
            name=f'{chosen_covid_data}',
            marker=dict(color='#342e37')
        ),
        secondary_y=False,
    )

    fig.update_layout(
        title_text=chosen_emotion.capitalize() + ' vs ' + chosen_covid_data
    )

    fig.update_xaxes(title_text='Dates')
    fig.update_yaxes(title_text=f'<b>{chosen_covid_data}</b>', secondary_y=False)
    fig.update_yaxes(title_text=f'<b>{chosen_emotion.capitalize()}</b>', secondary_y=True)
    fig.show()


def draw_saved_graph(chosen_emotion: str, chosen_covid_data: str):
    """Plots the COVID and emotional data from file.
    """
    fig = make_subplots(specs=[[{'secondary_y': True}]])
    start_date, end_date, emotion_data = get_emotion_from_file(chosen_emotion)
    covid_data = get_covid_data(start_date, end_date, chosen_covid_data)
    dates = get_desired_dates(start_date, end_date)

    fig.add_trace(
        go.Scatter(
            x=dates,
            y=emotion_data,
            name=f'{chosen_emotion.capitalize()}',
            marker=dict(color='#1A70C7'),
            line=dict(width=6)
        ),
        secondary_y=True,
    )

    fig.add_trace(
        go.Bar(
            x=dates,
            y=covid_data,
            name=f'{chosen_covid_data}',
            marker=dict(color='#342e37')
        ),
        secondary_y=False,
    )

    fig.update_layout(
        title_text=chosen_emotion.capitalize() + ' vs ' + chosen_covid_data
    )

    fig.update_xaxes(title_text='Dates')
    fig.update_yaxes(title_text=f'<b>{chosen_covid_data}</b>', secondary_y=False)
    fig.update_yaxes(title_text=f'<b>{chosen_emotion.capitalize()}</b>', secondary_y=True)
    fig.show()
