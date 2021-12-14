"""
Code for calculating the emotional index of tweets.
"""
from jellyfish import jaro_winkler_similarity as jaro_winkler
from tweet_data import to_twint
import datetime
import pandas


def get_lexicon_data(filename: str) -> pandas.DataFrame:
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

    df = pandas.DataFrame.from_dict(words_indices)
    df.index.name = 'emotion'
    return df


def clean_text(text: str) -> list[str]:
    """Return text as a list of lowercase words excluding punctuation, numbers, and emojis.
    """
    return ''.join(char for char in text if char.isalpha() or char == ' ').split()


def daily_emotions(tweet_tuple: tuple[datetime, list[str]], lexicon_data: pandas.DataFrame) -> \
        tuple[datetime, dict[str, float]]:
    """Return a dictionary mapping a single day of tweets to another dictionary mapping emotions to
    the sum of its value in the tweets.
    """
    day, tweets = tweet_tuple
    check_winkler = {}

    emotion_lexicon = (day, {'anger': 0, 'anticipation': 0, 'disgust': 0, 'fear': 0, 'joy': 0,
                             'negative': 0, 'positive': 0, 'sadness': 0, 'surprise': 0, 'trust': 0})

    for tweet in tweets:
        for word in clean_text(tweet):
            if word in lexicon_data.columns:
                for emotion in emotion_lexicon[1].keys():
                    emotion_lexicon[1][emotion] += lexicon_data[word][emotion]
            else:
                if word not in check_winkler:
                    check_winkler[word] = 0
                check_winkler[word] += 1

    for lexicon_word in lexicon_data.columns:
        to_pop = []
        for word in check_winkler:
            if jaro_winkler(lexicon_word, word) > 0.87:
                for emotion in emotion_lexicon[1].keys():
                    emotion_lexicon[1][emotion] += lexicon_data[lexicon_word][emotion] * check_winkler[word]
                to_pop.append(word)
        for word in to_pop:
            check_winkler.pop(word)

    return emotion_lexicon


def total_emotions(tweets: tuple[datetime, list[tuple[datetime, list[str]]]], save: bool) -> \
        dict[str, dict[str, float]]:
    """Return a dictionary mapping the days of the tweets to a dictionary mapping emotions to
    its value from the tweets of that day.
    """
    lexicon_data = get_lexicon_data('NRC-Emotion-Lexicon-Wordlevel-v0.92.txt')
    _, list_of_day_tuples = tweets
    week_to_emotion = {}

    for day_tuple in list_of_day_tuples:
        day, value = daily_emotions(day_tuple, lexicon_data)
        week_to_emotion[to_twint(day)] = value

    if save:
        save_to_raw_data(week_to_emotion)

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
