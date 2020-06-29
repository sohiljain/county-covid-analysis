import sys
import pandas as pd
from sqlalchemy import create_engine
import logging
import datetime


def historical_load():
    """
    Load historical data by parsing over all the columns
    """
    url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv"
    data = pd.read_csv(url)
    length = len(data.columns)
    df = extract_covid_count()
    format_str = '%m/%d/%y'  # The format

    for i in range(12, length - 2):
        df1 = data.iloc[:, [4, 10, i]]
        df1.columns = ['fips', 'county', 'cases']
        df1 = df1.dropna(subset=['fips'])
        df1['fips'] = df1['fips'].astype("Float32").astype("Int32").astype(str)
        df1['fips'] = df1['fips'].apply(lambda x: x.zfill(5))
        date_str = data.columns[i]  # The date - 29 Dec 2017
        datetime_obj = datetime.datetime.strptime(date_str, format_str).date()
        df1['dt'] = datetime_obj
        df2 = pd.concat([df, df1])
        df = df2

    return df


def extract_covid_count():
    """
    Load data in the last column that corresponds to last/current day
    :return:
    """
    url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv"
    data = pd.read_csv(url)
    length = len(data.columns)
    df = data.iloc[:, [4, 10, length - 1]]
    df.columns = ['fips', 'county', 'cases']
    date_str = data.columns.values[length - 1]
    format_str = '%m/%d/%y'  # The format
    datetime_obj = datetime.datetime.strptime(date_str, format_str).date()
    df['dt'] = datetime_obj
    df = df.dropna(subset=['fips'])
    df['fips'] = df['fips'].astype("Float32").astype("Int32").astype(str)
    df['fips'] = df['fips'].apply(lambda x: x.zfill(5))

    return df


def extract_population():
    """
    Extract population data
    """
    url = "https://www2.census.gov/programs-surveys/popest/tables/2010-2019/counties/totals/co-est2019-annres.xlsx"
    df_pop = pd.read_excel(url, skiprows=4, usecols="A,M", names=["county", "population_2019"], nrows=3142)
    df_pop['county'] = df_pop['county'].apply(lambda x: x.replace('.', '').replace(' County', '') + ", US")
    df_pop['population_2019'] = df_pop['population_2019'].astype("Int32")
    return df_pop


def transform_merge(df1, df2):
    final = pd.concat([df1, df2], join='inner', axis=1)
    return final


if __name__ == '__main__':

    # create connection to sqlite db
    db_connect = create_engine('sqlite:///covid_analysis.db')
    conn = db_connect.connect()

    sql_create = """create table if not exists covid (
    fips varchar,
    cases int,
    rate fload,
    dt date,
    county varchar
    )"""
    query = conn.execute(sql_create)
    logging.debug(query)

    # check if a parameter history is present to run historical load, else run current load
    if len(sys.argv) == 2 and sys.argv[1] == 'history':
        historical_load().to_sql('covid_count_tmp', conn, index=False, if_exists='replace')
    else:
        extract_covid_count().to_sql('covid_count_tmp', conn, index=False, if_exists='replace')

    extract_population().to_sql('county_population', conn, index=False, if_exists='replace')

    sql_create = """
    insert or replace into covid
    select distinct a.fips,
      a.cases,
      cast(a.cases*10000/b.population_2019 as float)/100 as rate,
      a.dt,
      a.county
    from covid_count_tmp a left join county_population b
        on a.county=b.county"""
    query = conn.execute(sql_create)
    logging.debug(query)