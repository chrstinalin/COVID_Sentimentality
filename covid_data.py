"""
Retrieves and filters the COVID-19 data from Ourworldindata.org.
"""
import pandas


def get_covid_data() -> pandas.DataFrame:
    """
    Retrieves owid-covid-data.csv and returns it as a DataFrame.
    """
    data = pandas.read_csv('https://covid.ourworldindata.org/data/owid-covid-data.csv')
    return data


def pretty(header: str) -> dict[str: str]:
    """
    Returns a header in a nicer format.
    """
    return ' '.join(header.split('_')).title()


def date_to_row(data: pandas.DataFrame, date_set: set[str], csv: bool, overwrite: bool) -> dict:
    """
    Returns a dictionary mapping desired dates to each numerical column's value.
    if save_to_csv, saves the processed data.
    """
    h_type = dict(data.dtypes)
    dates_dict = {}

    for _, row in data.iterrows():
        if overwrite or row['date'] not in date_set:

            if row['date'] not in dates_dict:
                dates_dict[row['date']] = {}
                for header in data.columns:
                    if h_type[header] != object:
                        dates_dict[row['date']][pretty(header)] = 0

            for header in data.columns:
                if h_type[header] != object and pandas.notnull(row[header]):
                    dates_dict[row['date']][pretty(header)] += row[header]

    if csv:
        df = pandas.DataFrame.from_dict(dates_dict)
        df.index.name = 'header'

        if not overwrite:
            df = process_data().merge(df, on='header')

        # noinspection PyTypeChecker
        df.to_csv('processed_covid_data.csv', index=overwrite)

    return dates_dict


def process_data() -> pandas.DataFrame:
    """
    Returns processed_covid_data as a DataFrame.
    """
    return pandas.read_csv('processed_covid_data.csv')


def overwrite_processed_covid_data(data: pandas.DataFrame) -> dict:
    """Fetches the newest version of the OWID Covid Data and overwrites the spreadsheet
        with newly processed values.
    """
    return date_to_row(data, set(), csv=True, overwrite=True)


def update_processed_covid_data(data: pandas.DataFrame, processed_data: pandas.DataFrame) -> dict:
    """Fetches the newest version of the OWID Covid Data and updates the processed spreadsheet
    with missing dates' values.
    """
    return date_to_row(data, set(processed_data.columns), csv=True, overwrite=False)
