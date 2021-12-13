"""
Code for calculating the emotional index of tweets.
"""
from jellyfish import jaro_winkler_similarity as jaro_winkler
from tweet_data import to_twint
import datetime
import pandas


def get_lexicon_data(filename: str) -> dict[str, dict]:
    """Retrieves the NRC Emotion Lexicon and creates a dictionary mapping each word to
    a dictionary mapping emotions to its value.
    """
    data = pandas.read_csv(filename, delim_whitespace=True, header=None)
    words_indices = {}

    for _, row in data.iterrows():
        word, emotion, value = str(row[0]), row[1], row[2]
        if word not in words_indices:
            words_indices[word] = {}
        words_indices[word][emotion] = value

    return words_indices


def clean_text(text: str) -> list[str]:
    """Return text as a list of lowercase words excluding punctuation, numbers, and emojis.
    """
    return ''.join(char for char in text if char.isalpha() or char == ' ').split()


def daily_average_emotions(tweet_tuple: tuple[datetime, list[str]]) -> \
        tuple[datetime, dict[str, float]]:
    """Return a dictionary mapping the day of the tweets to another dictionary mapping emotions to
    a sum of its average values in the tweets. The average (per tweet) is calculated by dividing the
    values of each emotion by the total number of words in the tweet.
    """
    lexicon_data = get_lexicon_data('NRC-Emotion-Lexicon-Wordlevel-v0.92.txt')
    day, tweets = tweet_tuple
    word_lexicon = {}

    emotion_lexicon = (day, {'anger': 0, 'anticipation': 0, 'disgust': 0, 'fear': 0, 'joy': 0,
                             'negative': 0, 'positive': 0, 'sadness': 0, 'surprise': 0, 'trust': 0})

    for tweet in tweets:
        for word in clean_text(tweet):

            if word in lexicon_data:
                word_lexicon = lexicon_data[word]
            else:
                for word_in_lexicon_data in lexicon_data:
                    if jaro_winkler(word_in_lexicon_data, word) > 0.80:
                        word_lexicon = lexicon_data[word_in_lexicon_data]

            for key in word_lexicon:
                emotion_lexicon[1][key] += word_lexicon[key]

    return emotion_lexicon


def total_average_emotions_per_tweet(tweets: tuple[datetime, list[tuple[datetime, list[str]]]]) -> \
        dict[str, dict[str, float]]:
    """Return a dictionary mapping a day of the week to a dictionary mapping emotions to
    its value from the tweets of that day.
    """
    _, list_of_day_tuples = tweets
    week_to_emotion = {}

    for day_tuple in list_of_day_tuples:
        day, value = daily_average_emotions(day_tuple)
        week_to_emotion[to_twint(day)] = value

    return week_to_emotion


def save_to_raw_data(data: dict[str, dict[str, float]]) -> None:
    """ Saves calculated emotional indices to tweet_emotional_index.csv.
    """
    df = pandas.DataFrame.from_dict(data)
    df.index.name = 'emotion'
    # noinspection PyTypeChecker
    df.to_csv('tweet_emotional_index.csv')


def pull_from_raw_data() -> dict[str, dict[str, float]]:
    """ Returns the data in tweet_emotional_index.csv.
    """
    return pandas.read_csv('tweet_emotional_index.csv').set_index('emotion').to_dict()
