################################################################################
#
# Package   : AlphaPy
# Module    : data
# Created   : July 11, 2013
#
# Copyright 2019 ScottFree Analytics LLC
# Mark Conway & Robert D. Scott II
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
################################################################################


#
# Imports
#

from alphapy.frame import Frame
from alphapy.frame import frame_name
from alphapy.frame import read_frame
from alphapy.globals import datasets
from alphapy.globals import ModelType
from alphapy.globals import Partition
from alphapy.globals import PD_INTRADAY_OFFSETS
from alphapy.globals import SSEP
from alphapy.globals import WILDCARD
from alphapy.space import Space
from alphapy.transforms import dateparts
from alphapy.transforms import timeparts

from datetime import datetime
from iexfinance.stocks import get_historical_data
from iexfinance.stocks import get_historical_intraday
from io import BytesIO
import logging
import numpy as np
import pandas as pd
pd.core.common.is_list_like = pd.api.types.is_list_like
import pandas_datareader.data as web
from polygon import RESTClient
import pytz
import re
import requests
from sklearn.preprocessing import LabelEncoder
import sys
import yfinance as yf


#
# Initialize logger
#

logger = logging.getLogger(__name__)


#
# Function get_data
#

def get_data(model, partition):
    r"""Get data for the given partition.

    Parameters
    ----------
    model : alphapy.Model
        The model object describing the data.
    partition : alphapy.Partition
        Reference to the dataset.

    Returns
    -------
    df_X : pandas.DataFrame
        The feature set.
    df_y : pandas.DataFrame
        The array of target values, if available.

    """

    logger.info("Loading Data")

    # Extract the model data

    directory = model.specs['directory']
    live_results = model.specs['live_results']
    run_dir = model.specs['run_dir']
    extension = model.specs['extension']
    features = model.specs['features']
    model_type = model.specs['model_type']
    separator = model.specs['separator']
    target = model.specs['target']

    # Initialize X and y

    df_X = pd.DataFrame()
    df_y = pd.DataFrame()

    # Read in the file

    filename = datasets[partition]
    data_dir = SSEP.join([directory, 'data'])
    df = read_frame(data_dir, filename, extension, separator)
    if df.empty:
        input_dir = SSEP.join([run_dir, 'input'])
        df = read_frame(input_dir, filename, extension, separator)

    # Get features and target

    if not df.empty:
        if target in df.columns:
            logger.info("Found target %s in data frame", target)
            # check if target column has NaN values
            nan_count = df[target].isnull().sum()
            logger.info("Found %d records with NaN target values", nan_count)
            # drop NA targets
            if not live_results or partition == Partition.train:
                df = df.dropna(subset=[target]).reset_index(drop=True)
                if nan_count > 0:
                    logger.info("Dropped %d records with NaN target values", nan_count)
            # assign the target column to y
            df_y = df[target]
            # encode label only for classification or system
            if model_type == ModelType.classification or model_type == ModelType.system:
                y = LabelEncoder().fit_transform(df_y)
                df_y = pd.DataFrame(y, columns=[target])
            # drop the target from the original frame
            df = df.drop([target], axis=1)
        else:
            logger.info("Target %s not found in %s", target, partition)
        # Extract features
        if features == WILDCARD:
            df_X = df
        else:
            df_X = df[features]

    # Labels are returned usually only for training data
    return df_X, df_y


#
# Function shuffle_data
#

def shuffle_data(model):
    r"""Randomly shuffle the training data.

    Parameters
    ----------
    model : alphapy.Model
        The model object describing the data.

    Returns
    -------
    model : alphapy.Model
        The model object with the shuffled data.

    """

    # Extract model parameters.

    seed = model.specs['seed']
    shuffle = model.specs['shuffle']

    # Extract model data.

    X_train = model.X_train

    # Shuffle data

    if shuffle:
        logger.info("Shuffling Training Data")
        np.random.seed(seed)
        np.random.shuffle(X_train)
        model.X_train = X_train
    else:
        logger.info("Skipping Shuffling")

    return model


#
# Function convert_data
#

def convert_data(df, intraday_data):
    r"""Convert the market data frame to canonical format.

    Parameters
    ----------
    df : pandas.DataFrame
        The intraday dataframe.
    intraday_data : bool
        Flag set to True if the frame contains intraday data.

    Returns
    -------
    df : pandas.DataFrame
        The canonical dataframe with date/time index.

    """

    # Create the date and time columns

    df['date'] = df.index
    df['date'] = pd.to_datetime(df['date']).dt.date
    if intraday_data:
        df['time'] = df.index
        df['time'] = pd.to_datetime(df['time']).dt.time

    # Add datetime columns

    # daily data
    df = pd.concat([df, dateparts(df, 'date')], axis=1)

    # intraday data
    if intraday_data:
        # Group by date first
        date_group = df.groupby('date')
        # Number the intraday bars
        df['barnumber'] = date_group.cumcount().astype(int)
        df['barpct'] = date_group['barnumber'].transform(lambda x: 100.0 * x / x.count())
        # Add progressive intraday columns
        df['opend'] = date_group['open'].transform('first')
        df['highd'] = date_group['high'].cummax()
        df['lowd'] = date_group['low'].cummin()
        df['closed'] = date_group['close'].transform('last')
        # Mark the end of the trading day
        df['endofday'] = False
        df.loc[date_group.tail(1).index, 'endofday'] = True
        # get time fields
        df = pd.concat([df, timeparts(df, 'time')], axis=1)

    # Drop date and time fields after extracting parts

    del df['date']
    if intraday_data:
        del df['time']

    # Make the numerical columns floating point

    cols_float = ['open', 'high', 'low', 'close', 'volume']
    df[cols_float] = df[cols_float].astype(float)

    # Forward-Fill prices and volume
    df.loc[:, cols_float] = df.loc[:, cols_float].ffill()

    # Order the frame by increasing date if necessary
    df = df.sort_index()
    return df


#
# Function convert_offset
#

def convert_offset(alias, mappings):
    r"""Convert the market data frame to canonical format.

    Parameters
    ----------
    alias : pandas.tseries.offsets
        Pandas offset alias.
    mappings : dict
        Mapping of offset alias time frame.

    Returns
    -------
    number : int
        The number of periods of the data to be retrieved.
    timespan : str
        The period of the data feed to be retrieved.

    """

    # Separate number and term

    match = re.match(r"(\d+)?(\w+)", alias)
    if match:
        number, term = match.groups()
        number = int(number) if number else 1

        # Convert term to timespan
        if term in mappings:
            timespan = mappings[term]
            return (number, timespan)
        else:
            raise ValueError(f"Unknown offset alias: {alias}")
    else:
        raise ValueError(f"Invalid offset alias: {alias}")


#
# Function get_eodhd_data
#

def get_eodhd_data(source, alphapy_specs, symbol, intraday_data, data_fractal,
                   from_date, to_date, lookback_period):
    r"""Get EODHD daily and intraday data.

    Parameters
    ----------
    source : str
        The data feed.
    alphapy_specs : dict
        The specifications for controlling the AlphaPy pipeline.
    symbol : str
        A valid stock symbol.
    intraday_data : bool
        If True, then get intraday data.
    data_fractal : str
        Pandas offset alias.
    from_date : str
        Starting date for symbol retrieval.
    to_date : str
        Ending date for symbol retrieval.
    lookback_period : int
        The number of periods of data to retrieve.

    Returns
    -------
    df : pandas.DataFrame
        The dataframe containing the intraday data.

    """

    # Set up parameters for EODHD API

    symbol = symbol.upper()

    mappings = {
        "min" : "m",
        "T"   : "m",
        "H"   : "h",
        "D"   : "d",
        "W"   : "w",
        "M"   : "m",
    }
    n_periods, period = convert_offset(data_fractal, mappings)

    #
    # Note: HTTP Request to EODHD API
    #
    # Examples:
    #
    # https://eodhd.com/api/eod/MCD.US?period=d&api_token=demo&fmt=csv
    #
    # https://eodhd.com/api/eod/MCD.US?from=2020-01-05&to=2020-02-10&period=d&api_token=647208fdeb65b4.31965673&fmt=json
    #

    df = pd.DataFrame()

    api_key = alphapy_specs['sources']['eodhd']['api_key']
    api_key_str = 'api_token=' + api_key
    format_str = 'fmt=csv'
    if intraday_data:
        url_base = f'https://eodhd.com/api/intraday/{symbol}?'
        tz_eastern = pytz.timezone('US/Eastern')
        from_obj = datetime.strptime(from_date, "%Y-%m-%d")
        from_obj_est = tz_eastern.localize(from_obj)
        from_unix_time = int(from_obj_est.timestamp())
        from_str = 'from=' + str(from_unix_time)
        to_obj = datetime.strptime(to_date, "%Y-%m-%d")
        to_obj_est = tz_eastern.localize(to_obj)
        to_unix_time  = int(to_obj_est.timestamp())
        to_str = 'to=' + str(to_unix_time)
        interval_str = 'interval=' + str(n_periods) + period
        url_str = '&'.join([api_key_str, from_str, to_str, interval_str, format_str])
    else:
        url_base = f'https://eodhd.com/api/eod/{symbol}?'
        from_str = 'from=' + from_date
        to_str = 'to=' + to_date
        period_str = 'period=' + period
        url_str = '&'.join([api_key_str, from_str, to_str, period_str, format_str])
    url = url_base + url_str

    response = requests.get(url).content
    df = pd.read_csv(BytesIO(response))
    df.columns = [col.lower() for col in df.columns]
    cols_ohlcv = ['open', 'high', 'low', 'close', 'volume']

    if intraday_data:
        col_dt = 'datetime'
        df[col_dt] = pd.to_datetime(df[col_dt], utc=True)
        df[col_dt] = df[col_dt].dt.tz_convert(tz_eastern)
        df[col_dt] = df[col_dt].dt.tz_localize(None)
    else:
        col_dt = 'date'
        df[col_dt] = pd.to_datetime(df[col_dt])

    cols_df = [col_dt] + cols_ohlcv
    df = df[cols_df]

    # Return the dataframe
    return df


#
# Function get_google_intraday_data
#

def get_google_intraday_data(symbol, lookback_period, fractal):
    r"""Get Google Finance intraday data.

    We get intraday data from the Google Finance API, even though
    it is not officially supported. You can retrieve a maximum of
    50 days of history, so you may want to build your own database
    for more extensive backtesting.

    Parameters
    ----------
    symbol : str
        A valid stock symbol.
    lookback_period : int
        The number of days of intraday data to retrieve, capped at 50.
    fractal : str
        The intraday frequency, e.g., "5m" for 5-minute data.

    Returns
    -------
    df : pandas.DataFrame
        The dataframe containing the intraday data.

    """

    # Google requires upper-case symbol, otherwise not found
    symbol = symbol.upper()
    # Initialize data frame
    df = pd.DataFrame()
    # Convert fractal to interval
    interval = 60 * int(re.findall(r'\d+', fractal)[0])
    # Google has a 50-day limit
    max_days = 50
    if lookback_period > max_days:
        lookback_period = max_days
    # Set Google data constants
    toffset = 7
    line_length = 6
    # Make the request to Google
    base_url = 'https://finance.google.com/finance/getprices?q={}&i={}&p={}d&f=d,o,h,l,c,v'
    url = base_url.format(symbol, interval, lookback_period)
    response = requests.get(url)
    # Process the response
    text = response.text.split('\n')
    records = []
    for line in text[toffset:]:
        items = line.split(',')
        if len(items) == line_length:
            dt_item = items[0]
            close_item = items[1]
            high_item = items[2]
            low_item = items[3]
            open_item = items[4]
            volume_item = items[5]
            if dt_item[0] == 'a':
                day_item = float(dt_item[1:])
                offset = 0
            else:
                offset = float(dt_item)
            dt = datetime.fromtimestamp(day_item + (interval * offset))
            dt = pd.to_datetime(dt)
            dt_date = dt.strftime('%Y-%m-%d')
            dt_time = dt.strftime('%H:%M:%S')
            record = (dt_date, dt_time, open_item, high_item, low_item, close_item, volume_item)
            records.append(record)
    # Create data frame
    cols = ['date', 'time', 'open', 'high', 'low', 'close', 'volume']
    df = pd.DataFrame.from_records(records, columns=cols)
    # Return the dataframe
    return df


#
# Function get_google_data
#

def get_google_data(source, alphapy_specs, symbol, intraday_data, data_fractal,
                    from_date, to_date, lookback_period):
    r"""Get data from Google.

    Parameters
    ----------
    source : str
        The data feed.
    alphapy_specs : dict
        The specifications for controlling the AlphaPy pipeline.
    symbol : str
        A valid stock symbol.
    intraday_data : bool
        If True, then get intraday data.
    data_fractal : str
        Pandas offset alias.
    from_date : str
        Starting date for symbol retrieval.
    to_date : str
        Ending date for symbol retrieval.
    lookback_period : int
        The number of periods of data to retrieve.

    Returns
    -------
    df : pandas.DataFrame
        The dataframe containing the market data.

    """

    df = pd.DataFrame()
    if intraday_data:
        # use internal function
        # df = get_google_intraday_data(symbol, lookback_period, data_fractal)
        logger.info("Google Finance API for intraday data no longer available")
    else:
        # Google Finance API no longer available
        logger.info("Google Finance API for daily data no longer available")
    return df


#
# Function get_iex_data
#

def get_iex_data(source, alphapy_specs, symbol, intraday_data, data_fractal,
                 from_date, to_date, lookback_period):
    r"""Get data from IEX.

    Parameters
    ----------
    source : str
        The data feed.
    alphapy_specs : dict
        The specifications for controlling the AlphaPy pipeline.
    symbol : str
        A valid stock symbol.
    intraday_data : bool
        If True, then get intraday data.
    data_fractal : str
        Pandas offset alias.
    from_date : str
        Starting date for symbol retrieval.
    to_date : str
        Ending date for symbol retrieval.
    lookback_period : int
        The number of periods of data to retrieve.

    Returns
    -------
    df : pandas.DataFrame
        The dataframe containing the market data.

    """

    symbol = symbol.upper()
    df = pd.DataFrame()

    if intraday_data:
        # use iexfinance function to get intraday data for each date
        df = pd.DataFrame()
        for d in pd.date_range(from_date, to_date):
            dstr = d.strftime('%Y-%m-%d')
            logger.info("%s Data for %s", symbol, dstr)
            try:
                df1 = get_historical_intraday(symbol, d, output_format="pandas")
                df1_len = len(df1)
                if df1_len > 0:
                    logger.info("%s: %d rows", symbol, df1_len)
                    df = df.append(df1)
                    df = pd.concat([df, df1])
                else:
                    logger.info("%s: No Trading Data for %s", symbol, dstr)
            except:
                iex_error = "*** IEX Intraday Data Error (check Quota) ***"
                logger.error(iex_error)
                sys.exit(iex_error)
    else:
        # use iexfinance function for historical daily data
        try:
            df = get_historical_data(symbol, from_date, to_date, output_format="pandas")
        except:
            iex_error = "*** IEX Daily Data Error (check Quota) ***"
            logger.error(iex_error)
            sys.exit(iex_error)
    return df


#
# Function get_pandas_data
#

def get_pandas_data(source, alphapy_specs, symbol, intraday_data, data_fractal,
                    from_date, to_date, lookback_period):
    r"""Get Pandas Web Reader data.

    Parameters
    ----------
    source : str
        The data feed.
    alphapy_specs : dict
        The specifications for controlling the AlphaPy pipeline.
    symbol : str
        A valid stock symbol.
    intraday_data : bool
        If True, then get intraday data.
    data_fractal : str
        Pandas offset alias.
    from_date : str
        Starting date for symbol retrieval.
    to_date : str
        Ending date for symbol retrieval.
    lookback_period : int
        The number of periods of data to retrieve.

    Returns
    -------
    df : pandas.DataFrame
        The dataframe containing the market data.

    """

    # Call the Pandas Web data reader.

    try:
        df = web.DataReader(symbol, source, from_date, to_date)
    except:
        df = pd.DataFrame()
        logger.info("Could not retrieve %s data with pandas-datareader", symbol.upper())

    return df


#
# Function get_polygon_data
#

def get_polygon_data(source, alphapy_specs, symbol, intraday_data, data_fractal,
                     from_date, to_date, lookback_period):
    r"""Get Polygon daily and intraday data.

    Parameters
    ----------
    source : str
        The data feed.
    alphapy_specs : dict
        The specifications for controlling the AlphaPy pipeline.
    symbol : str
        A valid stock symbol.
    intraday_data : bool
        If True, then get intraday data.
    data_fractal : str
        Pandas offset alias.
    from_date : str
        Starting date for symbol retrieval.
    to_date : str
        Ending date for symbol retrieval.
    lookback_period : int
        The number of periods of data to retrieve.

    Returns
    -------
    df : pandas.DataFrame
        The dataframe containing the intraday data.

    """

    # Set up parameters for Polygon API

    symbol = symbol.upper()

    mappings = {
        "min" : "minute",
        "T"   : "minute",
        "H"   : "hour",
        "D"   : "day",
        "W"   : "week",
        "M"   : "month",
        "Q"   : "quarter",
        "A"   : "year",
    }
    n_periods, period = convert_offset(data_fractal, mappings)

    #
    # Note: HTTP Request to Polygon API
    #
    # Example:
    #
    # https://api.polygon.io/v2/aggs/ticker/AAPL/range/5/minute/2023-01-09/2023-05-09
    # ?adjusted=true&sort=asc&limit=120&apiKey=_BynHqDfXhPoQcFf8Nb6hJzC_p67_5Sf1tn5ms
    #

    client = RESTClient(api_key=alphapy_specs['sources']['polygon']['api_key'])

    df = pd.DataFrame()
    aggs = []
    for a in client.list_aggs(ticker=symbol,
                              multiplier=n_periods,
                              timespan=period,
                              from_=from_date,
                              to=to_date,
                              limit=50000):
        aggs.append(a)
    df = pd.DataFrame(aggs)

    # Convert timestamp to datetime and adjust the format based on timespan
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
    if not intraday_data:
        df['date'] = df['datetime'].dt.date
        df.drop(columns=['datetime'], inplace=True)
        rename_column = 'date'
    else:
        rename_column = 'datetime'

    df.drop(columns=['timestamp', 'otc'], inplace=True)
    df = df[[rename_column] + [col for col in df.columns if col != rename_column]]

    # Return the dataframe
    return df


#
# Function get_yahoo_data
#

def get_yahoo_data(source, alphapy_specs, symbol, intraday_data, data_fractal,
                   from_date, to_date, lookback_period):
    r"""Get Yahoo daily and intraday data.

    Parameters
    ----------
    source : str
        The data feed.
    alphapy_specs : dict
        The specifications for controlling the AlphaPy pipeline.
    symbol : str
        A valid stock symbol.
    intraday_data : bool
        If True, then get intraday data.
    data_fractal : str
        Pandas offset alias.
    from_date : str
        Starting date for symbol retrieval.
    to_date : str
        Ending date for symbol retrieval.
    lookback_period : int
        The number of periods of data to retrieve.

    Returns
    -------
    df : pandas.DataFrame
        The dataframe containing the market data.

    """

    df = pd.DataFrame()
    data_fractal = data_fractal.lower()
    yahoo_fractals = {'min' : 'm',
                      'h'   : 'h',
                      'd'   : 'd',
                      'w'   : 'wk',
                      'm'   : 'mo'}
    pandas_offsets = yahoo_fractals.keys()
    fractal = [offset for offset in pandas_offsets if offset in data_fractal]
    if fractal:
        fvalue = fractal[0]
        yahoo_fractal = data_fractal.replace(fvalue, yahoo_fractals[fvalue])
        # intraday limit is 60 days
        ignore_tz = True if intraday_data else False
        df = yf.download(symbol, start=from_date, end=to_date, interval=yahoo_fractal,
                         ignore_tz=ignore_tz, threads=False)
        if df.empty:
            logger.info("Could not get data for: %s", symbol)
        else:
            df.index = df.index.tz_localize(None)
    else:
        logger.error("Valid Pandas Offsets for Yahoo Data are: %s", pandas_offsets)
    return df


#
# Data Dispatch Tables
#

data_dispatch_table = {'eodhd'   : get_eodhd_data,
                       'google'  : get_google_data,
                       'iex'     : get_iex_data,
                       'pandas'  : get_pandas_data,
                       'polygon' : get_polygon_data,
                       'yahoo'   : get_yahoo_data}


#
# Function assign_global_data
#

def assign_global_data(df, symbol, gspace, fractal):
    r"""Create global pointer to dataframe.

    Parameters
    ----------
    df : pandas.DataFrame
        The dataframe for the given symbol.
    symbol : str
        Pandas offset alias.
    gspace : alphapy.Space
        AlphaPy data taxonomy data source and subject.
    fractal : str
        Pandas offset alias.

    Returns
    -------
    df : pandas.DataFrame
        The dataframe for the given symbol.

    """
    try:
        space = Space(gspace.subject, gspace.source, fractal)
        _ = Frame(symbol.lower(), space, df)
    except:
        logger.error("Could not allocate Frame for: %s", symbol.upper())
    return df


#
# Function standardize_data
#

def standardize_data(symbol, gspace, df, fractal, intraday_data):
    r"""Get data from an external feed.

    Parameters
    ----------
    symbol : str
        Pandas offset alias.
    gspace : alphapy.Space
        AlphaPy data taxonomy data source and subject.
    df : pandas.DataFrame
        The raw output dataframe from the market datafeed.
    fractal : str
        Pandas offset alias.
    intraday_data : bool
        If True, then get intraday data.

    Returns
    -------
    df : pandas.DataFrame
        The standardized output dataframe for the market data.

    """

    # convert data to canonical form
    df = convert_data(df, intraday_data)
    # create global pointer to dataframe
    df = assign_global_data(df, symbol, gspace, fractal)
    # return dataframe
    return df


#
# Function get_market_data
#

def get_market_data(alphapy_specs, model, market_specs, group,
                    lookback_period, intraday_data=False, local_dir=''):
    r"""Get data from an external feed.

    Parameters
    ----------
    alphapy_specs : dict
        The specifications for controlling the AlphaPy pipeline.
    model : alphapy.Model
        The model object describing the data.
    market_specs : dict
        The specifications for controlling the MarketFlow pipeline.
    group : alphapy.Group
        The group of symbols.
    lookback_period : int
        The number of periods of data to retrieve.
    intraday_data : bool
        If True, then get intraday data.
    local_dir : str
        Local data directory, if needed.
    """

    # Unpack market specifications

    data_fractal = market_specs['data_fractal']
    feature_fractals = market_specs['fractals']
    from_date = market_specs['data_start_date']
    to_date = market_specs['data_end_date']
    start_time = datetime.strptime(market_specs['data_start_time'], '%H:%M').time()
    end_time = datetime.strptime(market_specs['data_end_time'], '%H:%M').time()

    # Unpack model specifications

    extension = model.specs['extension']
    separator = model.specs['separator']

    # Unpack group elements

    gspace = group.space
    gsubject = gspace.subject
    gsource = gspace.source

    # Determine the feed source

    if intraday_data:
        # intraday data (date and time)
        logger.info("Source [%s] Intraday Data [%s] for %d days",
                    gsource, data_fractal, lookback_period)
    else:
        # daily data or higher (date only)
        logger.info("Source [%s] Daily Data [%s] for %d days",
                    gsource, data_fractal, lookback_period)

    # Get the data from the specified data feed

    df = pd.DataFrame()
    remove_list = []

    for symbol in group.members:
        logger.info("Getting %s data from %s to %s",
                    symbol.upper(), from_date, to_date)
        # Locate the data source
        if gsource == 'data':
            # locally stored intraday or daily data
            dspace = Space(gsubject, gsource, data_fractal)
            fname = frame_name(symbol, dspace)
            df = read_frame(local_dir, fname, extension, separator)
        elif gsource in data_dispatch_table.keys():
            df = data_dispatch_table[gsource](gsource,
                                              alphapy_specs,
                                              symbol,
                                              intraday_data,
                                              data_fractal,
                                              from_date,
                                              to_date,
                                              lookback_period)
        else:
            raise ValueError("Unsupported Data Source: %s", gsource)
        # Now that we have content, standardize the data
        if not df.empty:
            df = df.copy()
            logger.info("Rows: %d [%s]", len(df), data_fractal)
            # reset the index to find the correct datetime column
            df.reset_index(inplace=True)
            df.columns = df.columns.str.lower()
            # find date or datetime column
            dt_cols = ['datetime', 'date']
            dt_index = None
            if df.index.name:
                df.index.name = df.index.name.lower()
                dt_index = [x for x in dt_cols if df.index.name == x]
            else:
                dt_column = [x for x in df.columns if x in dt_cols]
            # Set the dataframe's index to the relevant column
            if not dt_index:
                if dt_column:
                    df.set_index(pd.DatetimeIndex(pd.to_datetime(df[dt_column[0]])),
                                                  drop=True, inplace=True)
                else:
                    raise ValueError("Dataframe must have a datetime or date column")
            # drop any remaining date or index columns
            df.drop(columns=dt_cols, inplace=True, errors='ignore')
            df.drop(columns=['index'], inplace=True, errors='ignore')
            # deduplicate in case we have data overlap
            df = df.loc[~df.index.duplicated(keep='first')]
            # scope dataframe in time range
            if intraday_data and start_time and end_time:
                mask = (df.index.time >= start_time) & (df.index.time <= end_time)
                df = df.loc[mask]
            # scope dataframe in date range
            assert df.index.is_unique, "Index has duplicate values"
            df = df[from_date:to_date]
            # register the dataframe in the global namespace
            df = standardize_data(symbol, gspace, df, data_fractal, intraday_data)
            # resample data and drop any NA values
            for ff in feature_fractals:
                if ff != data_fractal:
                    df_rs = df.resample(ff).agg({'open'   : 'first',
                                                 'high'   : 'max',
                                                 'low'    : 'min',
                                                 'close'  : 'last',
                                                 'volume' : 'sum'})
                    df_rs.dropna(axis=0, how='any', inplace=True)
                    logger.info("Rows: %d [%s] resampled", len(df_rs), ff)
                    # standardize resampled data
                    intraday_fractal = any(substring in ff for substring in PD_INTRADAY_OFFSETS)
                    df_rs = standardize_data(symbol, gspace, df_rs, ff, intraday_fractal)
        else:
            logger.info("No DataFrame for %s", symbol.upper())
            remove_list.append(symbol)

    # Remove any group members not found

    if remove_list:
        group.remove(remove_list)

    return
