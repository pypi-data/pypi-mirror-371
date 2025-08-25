"""
Package   : AlphaPy
Module    : mflow_main
Created   : July 11, 2013

Copyright 2022 ScottFree Analytics LLC
Mark Conway & Robert D. Scott II

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


#
# Suppress Warnings
#

import warnings

warnings.simplefilter(action='ignore', category=DeprecationWarning)
warnings.simplefilter(action='ignore', category=FutureWarning)


#
# Imports
#

import argparse
import datetime
import logging
import os
import pandas as pd
import shutil
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
import sys
import yaml

from alphapy.alphapy_main import get_alphapy_config
from alphapy.alphapy_main import main_pipeline
from alphapy.data import get_market_data
from alphapy.frame import Frame
from alphapy.frame import frame_name
from alphapy.frame import write_frame
from alphapy.globals import BarType
from alphapy.globals import ModelType
from alphapy.globals import LOFF, ROFF, SSEP, USEP
from alphapy.globals import PD_INTRADAY_OFFSETS
from alphapy.group import Group
from alphapy.metalabel import add_vertical_barrier
from alphapy.metalabel import get_bins
from alphapy.metalabel import get_events
from alphapy.metalabel import get_threshold_events
from alphapy.model import get_model_config
from alphapy.model import Model
from alphapy.portfolio import gen_portfolios
from alphapy.space import Space
from alphapy.system import run_system
from alphapy.system import System
from alphapy.system import SystemRank
from alphapy.transforms import netreturn
from alphapy.utilities import datetime_stamp
from alphapy.utilities import most_recent_file
from alphapy.utilities import subtract_days
from alphapy.utilities import valid_date
from alphapy.variables import vapply


#
# Initialize logger
#

logger = logging.getLogger(__name__)


#
# Function get_market_config
#

def get_market_config(directory='.'):
    r"""Read the configuration file for MarketFlow.

    Parameters
    ----------
    directory : str
        The location of the configuration file.

    Returns
    -------
    cfg : dict
        The original configuration specification.
    specs : dict
        The parameters for controlling MarketFlow.

    """

    logger.info('*'*80)
    logger.info("MarketFlow Configuration")

    # Read the configuration file

    full_path = SSEP.join([directory, 'config', 'market.yml'])
    with open(full_path, 'r') as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

    # Store configuration parameters in dictionary

    specs = {}

    #
    # Section: portfolio
    #

    logger.info("Getting Portfolio Parameters")
    try:
        specs['portfolio'] = cfg['portfolio']
    except:
        raise ValueError("No Portfolio Parameters Found")
    
    #
    # Section: system or ranking
    #

    logger.info("Checking for System and Ranking Parameters")

    system_present = 'system' in cfg
    ranking_present = 'ranking' in cfg

    if system_present and ranking_present:
        raise ValueError("Both System and Ranking Parameters Found - Only one is allowed")
    elif not system_present and not ranking_present:
        raise ValueError("Neither System nor Ranking Parameters Found - One is required")
    else:
        # Only one of the sections is present, so proceed to get that section
        if system_present:
            logger.info("Getting System Parameters")
            specs['system'] = cfg['system']
        else:  # ranking_present must be True here
            logger.info("Getting Ranking Parameters")
            specs['ranking'] = cfg['ranking']

    #
    # Section: data
    #

    data_section = cfg['data']
    specs['data_source'] = data_section['data_source']

    # Fractals must conform to the pandas offset format

    fractal = data_section['data_fractal']
    try:
        data_fractal_td = pd.to_timedelta(fractal)
    except:
        raise ValueError("Fractal [%s] is an invalid pandas offset" % fractal)
    specs['data_fractal'] = fractal

    data_history = data_section['data_history']
    if not data_history:
        data_history = 0

    start_date = data_section['data_start_date']
    end_date = data_section['data_end_date']

    if not start_date or not end_date:
        data_history_dt = pd.to_timedelta(data_history, unit='d')
        today_date_dt = pd.to_datetime('today')
        if start_date:
            start_date_dt = pd.to_datetime(start_date)
            if data_history > 0:
                end_date_dt = start_date_dt + data_history_dt
                end_date_dt = today_date_dt if end_date_dt > today_date_dt else end_date_dt
            else:
                end_date_dt = today_date_dt
        elif data_history > 0:
            if end_date:
                end_date_dt = pd.to_datetime(end_date)
                start_date_dt = end_date_dt - data_history_dt
            else:
                end_date_dt = today_date_dt
                start_date_dt = end_date_dt - data_history_dt
        else:
            raise ValueError("Either parameter data_start_date or data_history is required")
        start_date = start_date_dt.strftime('%Y-%m-%d')
        end_date = end_date_dt.strftime('%Y-%m-%d')

    specs['data_history'] = data_history
    specs['data_start_date'] = start_date
    specs['data_end_date'] = end_date
    specs['data_start_time'] = data_section['data_start_time']
    specs['data_end_time'] = data_section['data_end_time']
    specs['forecast_period'] = data_section['forecast_period']
    specs['predict_history'] = data_section['predict_history']
    specs['subject'] = data_section['subject']
    specs['target_group'] = data_section['target_group']
    specs['cohort_group'] = data_section['cohort_group']

    #
    # Section: Bar Type, Features and Fractals
    #

    logger.info("Getting Bar Type")

    try:
        specs['bar_type'] = BarType[cfg['bar_type']]
    except:
        logger.info("No valid bar type was specified. Default: time")
        specs['bar_type'] = BarType.time

    logger.info("Getting Features")
    specs['features'] = cfg['features']

    logger.info("Getting Fractals")

    fractals = list(specs['features'].keys())
    if len(fractals) > 1 and specs['bar_type'] != BarType.time:
        raise ValueError("Multiple Fractals valid only on time bars")
    
    fractal_dict = {}
    for frac in fractals:
        try:
            td = pd.to_timedelta(frac)
            fractal_dict[td] = frac
        except:
            raise ValueError("Fractal [%s] is an invalid pandas offset" % frac)
    
    # sort by ascending fractal
    fractals_sorted = dict(sorted(fractal_dict.items()))
    # store features sorted by fractal
    feature_fractals = list(fractals_sorted.values())
    # first (lowest) feature fractal must be >= data fractal
    if list(fractals_sorted)[0] < data_fractal_td:
        raise ValueError("Lowest feature fractal [%s] must >= data fractal [%s]" %
                         (feature_fractals[0], specs['data_fractal']))
    # assign to market specifications
    specs['fractals'] = feature_fractals

    #
    # Section: functions
    #

    logger.info("Getting Variable Functions")
    try:
        specs['functions'] = cfg['functions']
    except:
        logger.info("No Variable Functions Found")
        specs['functions'] = {}

    #
    # Log the market parameters
    #

    logger.info('MARKET PARAMETERS:')
    logger.info('bar_type         = %s', specs['bar_type'])
    logger.info('cohort_group     = %s', specs['cohort_group'])
    logger.info('data_end_date    = %s', specs['data_end_date'])
    logger.info('data_end_time    = %s', specs['data_end_time'])
    logger.info('data_fractal     = %s', specs['data_fractal'])
    logger.info('data_history     = %d', specs['data_history'])
    logger.info('data_source      = %s', specs['data_source'])
    logger.info('data_start_date  = %s', specs['data_start_date'])
    logger.info('data_start_time  = %s', specs['data_start_time'])
    logger.info('features         = %s', specs['features'])
    logger.info('forecast_period  = %d', specs['forecast_period'])
    logger.info('fractals         = %s', specs['fractals'])
    logger.info('portfolio        = %s', specs['portfolio'])
    logger.info('predict_history  = %d', specs['predict_history'])
    if ranking_present:
        specs['ranking']['forecast_period'] = specs['forecast_period']
        logger.info('ranking      = %s', specs['ranking'])
    logger.info('subject          = %s', specs['subject'])
    if system_present:
        logger.info('system       = %s', specs['system'])
    logger.info('target_group     = %s', specs['target_group'])

    # Market Specifications
    return cfg, specs


#
# Function set_targets_ranking
#

def set_targets_ranking(model, df, ranking_specs):
    r"""Set the Learn-to-Rank (LTR) targets.

    Parameters
    ----------
    model : alphapy.Model
        The model specifications.
    df : pandas.DataFrame
        The dataframe for ranking.
    ranking_specs : dict
        Ranking model specifications.

    Returns
    -------
    df : pandas.DataFrame
        The dataframe with the shifted target column.

    """

    logger.info("Setting Learn-To-Rank (LTR) Targets")

    # Unpack model specifications
    target = model.specs['target']

    # Unpack ranking specifications
    forecast_period = ranking_specs['forecast_period']

    # Shift the target column
    df[target] = df[target].shift(-forecast_period)

    return df


#
# Function set_targets_metalabel
#

def set_targets_metalabel(model, df, system_specs):
    r"""Set classification targets

    1. Extract the signal for long and short entries.
    2. Run the Triple Barrier Method analysis.

    Parameters
    ----------
    model : alphapy.Model
        The model specifications.
    df : pandas.DataFrame
        The dataframe to assign metalabels.
    system_specs : dict
        Trade management specifications.

    Returns
    -------
    df_meta : pandas.DataFrame
        The dataframe containing TBM returns, target, and labels

    """

    logger.info("Setting Metalabel Targets")

    # Unpack model specifications
    target = model.specs['target']

    # Unpack trading specifications

    signal_long = system_specs['signal_long']
    signal_short = system_specs['signal_short']
    forecast_period = system_specs['forecast_period']
    profit_factor = system_specs['profit_factor']
    stoploss_factor = system_specs['stoploss_factor']
    trade_fractal = system_specs['fractal']

    # Find the patterns (signals) in the dataframe.
    
    nrows = df.shape[0]

    if signal_long:
        long_col = USEP.join([signal_long, trade_fractal])
        long_label = 1
        df.loc[df[long_col], 'side'] = long_label
        npats = df[df['side'] == long_label].shape[0]
        logger.info("%d Long Patterns Found in %d Rows", npats, nrows)

    if signal_short:
        short_col = USEP.join([signal_short, trade_fractal])
        short_label = -1
        df.loc[df[short_col], 'side'] = short_label
        npats = df[df['side'] == short_label].shape[0]
        logger.info("%d Short Patterns Found in %d Rows", npats, nrows)

    # Lag the signal.
    df['side'] = df['side'].shift(1)

    # Get the CUSUM events.

    col_close = USEP.join(['close', trade_fractal])
    ds_close = df[col_close]
    cusum_events = get_threshold_events(ds_close, 0)

    # Establish the vertical barriers.
    vertical_barriers = add_vertical_barrier(cusum_events, ds_close, forecast_period,
                                             trade_fractal)

    # Set the Triple Barrier Method (TBM) events.

    df_tbm = get_events(ds_close,
                        cusum_events,
                        [profit_factor, stoploss_factor],
                        vertical_barriers,
                        df['side'])

    # Assign labels based on returns.
    df_labels = get_bins(df_tbm, ds_close)

    # Evaluate the primary model.

    primary_forecast = pd.DataFrame(df_labels['metalabel'])
    primary_forecast['pred'] = 1
    primary_forecast.columns = ['actual', 'pred']

    actual = primary_forecast['actual']
    pred = primary_forecast['pred']

    logger.info("Evaluating Primary Model")
    logger.info("Classification Report:")
    class_report = classification_report(y_true=actual, y_pred=pred, zero_division=0.0)
    logger.info(f"\n{class_report}")
    logger.info(f"Confusion Matrix:")
    logger.info(f"\n{confusion_matrix(actual, pred)}")
    logger.info(f"Accuracy: {accuracy_score(actual, pred)}")

    # Filter the dataframe with the events for the secondary model.

    df_meta = df.loc[df_labels.index, :].copy()
    df_meta[target] = df_labels[target]

    return df_meta


#
# Function prepare_data
#

def prepare_data(model, dfs, market_specs):
    r"""Prepare the model for training and validation.

    Parameters
    ----------
    model : alphapy.Model
        The model specifications.
    dfs : list
        The list of pandas dataframes to analyze.
    market_specs : dict
        Portfolio and system specifications.

    """

    logger.info("Preparing the Model")

    # Unpack model data

    test_file = model.test_file
    train_file = model.train_file

    # Unpack model specifications

    run_dir = model.specs['run_dir']
    extension = model.specs['extension']
    model_type = model.specs['model_type']
    predict_date = model.specs['predict_date']
    predict_mode = model.specs['predict_mode']
    rank_group_id = model.specs['rank_group_id']
    rank_group_size = model.specs['rank_group_size']
    seed = model.specs['seed']
    separator = model.specs['separator']
    target = model.specs['target']
    train_date = model.specs['train_date']

    # Unpack market specifications

    predict_history = market_specs['predict_history']
    forecast_period = market_specs['forecast_period']

    # Calculate split date

    logger.info("Analysis Dates")
    split_date = subtract_days(predict_date, predict_history)

    # Create dataframes

    if predict_mode:
        # create predict frame
        logger.info("Split Date for Prediction Mode: %s", split_date)
        predict_frame = pd.DataFrame()
    else:
        # create train and test frames
        logger.info("Split Date for Training Mode: %s", predict_date)
        train_frame = pd.DataFrame()
        test_frame = pd.DataFrame()

    #
    # For the Classification Metamodel, we are creating a target variable
    # based on whether the trade was successful. If the trade is profitable,
    # then the target is 1 else 0. Note that we are using the side feature
    # (trade direction) as input into the model.
    #
    # For the Learn-To-Rank Model, the target variable is typically
    # represented by returns over a certain period of time.
    #

    for df in dfs:
        # subset each individual frame and add to the master frame
        symbol = df['symbol'].iloc[0].upper()
        if not df.empty:
            # set model targets based on model type
            if model_type == ModelType.ranking:
                ranking_specs = market_specs['ranking']
                df = set_targets_ranking(model, df, ranking_specs)
            elif model_type == ModelType.system:
                system_specs = market_specs['system']
                df = set_targets_metalabel(model, df, system_specs)
            elif model_type == ModelType.classification or model_type == ModelType.regression:
                # shift target column back by the number of forecast periods
                df[target] = df[target].shift(-forecast_period)
                # count patterns found for classification            
                if model_type == ModelType.classification:
                    rows_old = df.shape[0]
                    rows_new = df[target].sum()
                    logger.info("%d Patterns Found in %d Rows", rows_new, rows_old)
            else:
                raise ValueError("Unsupported Model Type")
            # process each symbol
            first_date = df.index[0]
            last_date = df.index[-1]
            logger.info("Processing %s from %s to %s", symbol, first_date, last_date)
            # split the dataframe
            if predict_mode:
                new_predict = df.loc[(df.index >= split_date) & (df.index <= last_date)].copy()
                new_predict = new_predict.dropna(subset=[target])
                if len(new_predict) > 0:
                    predict_frame = pd.concat([predict_frame, new_predict])
                else:
                    logger.info("%s Prediction Frame has zero rows. Check prediction date.", symbol)
            else:
                # split data into train and test
                new_train = df.loc[(df.index >= first_date) & (df.index < predict_date)].copy()
                if not new_train.empty:
                    # check if target column has NaN values
                    nan_count = new_train[target].isnull().sum()
                    if nan_count > 0:
                        logger.info("%s has %d train records with a NaN target.", symbol, nan_count)
                    # drop records with NaN values in target column
                    new_train = new_train.dropna(subset=[target])
                    train_frame = pd.concat([train_frame, new_train])
                    # get test frame
                    new_test = df.loc[(df.index >= predict_date) & (df.index <= last_date)]
                    if not new_test.empty:
                        # check if target column has NaN values
                        nan_count = new_test[target].isnull().sum()
                        forecast_check = forecast_period - 1
                        if nan_count != forecast_check:
                            logger.info("%s has %d test records with a NaN target.", symbol, nan_count)
                        # append selected records to the test frame
                        test_frame = pd.concat([test_frame, new_test])
                    else:
                        logger.info("%s Testing Frame has zero rows. Check prediction date.", symbol)
                else:
                    logger.info("%s Training Frame has zero rows. Check data source.", symbol)
        else:
            logger.info("%s Dataframe is empty", symbol)

    # Convert column names from special characters

    def new_col_name(col_name):
        start = col_name.find(LOFF)
        end = col_name.find(ROFF)
        lag_string = col_name[start:end+1]
        lag_value = lag_string[1:-1]
        if lag_value:
            new_name = ''.join([col_name.replace(lag_string, ''), '_lag', lag_value])
        else:
            new_name = col_name
        return new_name

    new_columns = [new_col_name(x) for x in train_frame.columns]
    train_frame.columns = new_columns
    if not test_frame.empty:
        test_frame.columns = new_columns

    # Take random samples of each dataframe.

    if model_type == ModelType.ranking:
        # Adjust the rank group size if necessary
        n_symbols = len(dfs)
        if n_symbols < rank_group_size:
            logger.info("Ranking Group Size %d > Number of Symbols %d",
                        rank_group_size, n_symbols)
        n_samples = min(rank_group_size, n_symbols)
        logger.info("Random Sampling %d Rows for Ranking", n_samples)
        # Sample the dataframes
        if not test_frame.empty:
            test_frame = test_frame.groupby(rank_group_id).sample(n=n_samples, random_state=seed)
        if not predict_mode and not train_frame.empty:
            train_frame = train_frame.groupby(rank_group_id).sample(n=n_samples, random_state=seed)

    # Write out the frames for input into the AlphaPy pipeline

    directory = SSEP.join([run_dir, 'input'])
    if predict_mode:
        # write out the predict frame
        test_frame.sort_index(inplace=True)
        write_frame(test_frame, directory, test_file, extension, separator,
                    index=True, index_label='date')
    else:
        # write out the train and test frames
        train_frame.sort_index(inplace=True)
        write_frame(train_frame, directory, train_file, extension, separator,
                    index=True, index_label='date')
        if not test_frame.empty:
            test_frame = test_frame.dropna(subset=[target])
            test_frame.sort_index(inplace=True)
            write_frame(test_frame, directory, test_file, extension, separator,
                        index=True, index_label='date')
    return


#
# Function get_cohort_returns
#

def get_cohort_returns(dfs, group, fractal):
    r"""Calculate returns for the cohorts.

    Parameters
    ----------
    dfs : list
        The list of pandas dataframes to apply the cohort returns.
    group : alphapy.Group
        The cohort group for calculating returns.
    fractal : str
        Pandas offset alias.

    """

    logger.info("Calculating Cohort Returns")

    # Get cohort group information

    gspace = group.space
    gsubject = gspace.subject
    gsource = gspace.source
    symbols = [item.lower() for item in group.members]

    #
    # For each frame, calculate the difference in returns
    #

    col_roi = USEP.join(['roi', '1', fractal])
    for symbol in symbols:
        fspace = Space(gsubject, gsource, fractal)
        fname = frame_name(symbol.lower(), fspace)
        if fname in Frame.frames:
            df_cohort = Frame.frames[fname].df
            if not df_cohort.empty:
                roi_cohort = netreturn(df_cohort, 'close')
                col_roi_symbol = USEP.join([col_roi, symbol])
                for df in dfs:
                    df[col_roi_symbol] = df[col_roi] - roi_cohort
            else:
                logger.info("Empty Dataframe for %s [%s]", symbol, fractal)
        else:
            logger.info("Dataframe Not Found for %s [%s]", symbol, fractal)               
    return


#
# Function market_pipeline
#

def market_pipeline(alphapy_specs, model, market_specs):
    r"""Market Flow Pipeline

    Parameters
    ----------
    alphapy_specs : dict
        The specifications for controlling the AlphaPy pipeline.
    model : alphapy.Model
        The model object for AlphaPy.
    market_specs : dict
        The specifications for controlling the MarketFlow pipeline.

    Returns
    -------
    model : alphapy.Model
        The final results are stored in the model object.

    Notes
    -----
    (1) Define a group.
    (2) Get the market data.
    (3) Apply system features.
    (4) Create an analysis.
    (5) Run the analysis, which calls AlphaPy.

    """

    logger.info("Running Market Flow Pipeline")

    # Get model specifications

    model_type = model.specs['model_type']
    predict_mode = model.specs['predict_mode']
    target = model.specs['target']

    # Get data specifications

    cohort_group = market_specs['cohort_group']
    data_fractal = market_specs['data_fractal']
    data_history = market_specs['data_history']
    data_source = market_specs['data_source']
    forecast_period = market_specs['forecast_period']
    fractals = market_specs['fractals']
    functions = market_specs['functions']
    predict_history = market_specs['predict_history']
    subject = market_specs['subject']
    target_group = market_specs['target_group']
    trade_fractal = fractals[0]

    # Get system and ranking specifications

    if model_type == ModelType.ranking:
        ranking_specs = market_specs['ranking']
        ranking_specs['forecast_period'] = forecast_period
        ranking_specs['fractal'] = trade_fractal
        system_name = ranking_specs['system_name']
    else:
        system_specs = market_specs['system']
        system_specs['predict_history'] = predict_history
        system_specs['forecast_period'] = forecast_period
        system_specs['fractal'] = trade_fractal
        system_name = system_specs['system_name']

    # Get AlphaPy specifications
    data_dir = alphapy_specs['data_dir']

    # Set the target group and space

    group = Group.groups[target_group]
    group.space = Space(subject, data_source, trade_fractal)
    logger.info("Group Space: %s", group.space)
    logger.info("All Symbols: %s", group.members)

    # Set the cohort group and space

    try:
        group_cohort = Group.groups[cohort_group]
        group_cohort.space = Space(subject, data_source, trade_fractal)
        logger.info("Cohort Group Space: %s", group_cohort.space)
        logger.info("Cohort Symbols: %s", group_cohort.members)
    except:
        group_cohort = None

    # Determine whether or not this is an intraday analysis.

    intraday = any(substring in data_fractal for substring in PD_INTRADAY_OFFSETS)

    # Get the market data. If we can't get all the data, then
    # predict_history resets to the actual history obtained.

    lookback = predict_history if predict_mode else data_history
    local_dir = SSEP.join([data_dir, subject, trade_fractal])
    get_market_data(alphapy_specs, model, market_specs, group,
                    lookback, intraday, local_dir=local_dir)
    if group_cohort:
        get_market_data(alphapy_specs, model, market_specs, group_cohort,
                        lookback, intraday, local_dir=local_dir)

    # Apply the features to all frames, including the signals just for the
    # target fractal.

    dfs = vapply(group, market_specs, functions)

    # Apply the cohort returns to all frames.

    if group_cohort:
        get_cohort_returns(dfs, group_cohort, trade_fractal)

    # Prepare the data based on the model type.
    prepare_data(model, dfs, market_specs)

    # Run the AlphaPy model pipeline.
    model = main_pipeline(alphapy_specs, model)

    # Run a system or ranking model.

    if model_type == ModelType.ranking or model_type == ModelType.system:
        logger.info('*'*80)
        if model_type == ModelType.ranking:
            logger.info("Running the Ranking System")
            logger.info('*'*80)
            logger.info("System Name     : %s", ranking_specs['system_name'])
            logger.info("Forecast Period : %s", forecast_period)
            logger.info("Algorithm       : %s", ranking_specs['algo'])
            logger.info("Long Rank       : %s", ranking_specs['long_rank'])
            logger.info("Long Score      : %s", ranking_specs['long_score'])
            logger.info("Short Rank      : %s", ranking_specs['short_rank'])
            logger.info("Short Score     : %s", ranking_specs['short_score'])
            logger.info("Trade Fractal   : %s", trade_fractal)
            system = SystemRank(**ranking_specs)
        if model_type == ModelType.system:
            logger.info("Running the Trading System")
            logger.info('*'*80)
            logger.info("System Name      : %s", system_specs['system_name'])
            logger.info("Forecast Period  : %s", forecast_period)
            logger.info("Predict History  : %s", predict_history)
            logger.info("Profit Factor    : %s", system_specs['profit_factor'])
            logger.info("Stop Loss Factor : %s", system_specs['stoploss_factor'])
            logger.info("Algorithm        : %s", system_specs['algo'])
            logger.info("Probability Min  : %s", system_specs['prob_min'])
            logger.info("Probability Max  : %s", system_specs['prob_max'])
            logger.info("Trade Fractal    : %s", trade_fractal)
            system = System(**system_specs)
        # Run the system and generate the portfolio.
        df_trades_base, df_trades_prob = run_system(model, system, group, intraday)
        if df_trades_base.empty:
            logger.info("No trades to generate a portfolio")
        else:
            portfolio_specs = market_specs['portfolio']
            gen_portfolios(model, system_name, portfolio_specs, group, df_trades_base, df_trades_prob)

    # Return the completed model.
    return model


#
# Function main
#

def main(args=None):
    r"""MarketFlow Main Program

    Notes
    -----
    (1) Initialize logging.
    (2) Parse the command line arguments.
    (3) Get the market configuration.
    (4) Get the model configuration.
    (5) Create the model object.
    (6) Call the main MarketFlow pipeline.

    Raises
    ------
    ValueError
        Training date must be before prediction date.

    """

    # Argument Parsing

    parser = argparse.ArgumentParser(description="MarketFlow Parser")
    parser.add_argument("-d", "--debug", action="store_true", default=False)
    parser.add_argument('--pdate', dest='predict_date',
                        help="prediction date is in the format: YYYY-MM-DD",
                        required=False, type=valid_date)
    parser.add_argument('--tdate', dest='train_date',
                        help="training date is in the format: YYYY-MM-DD",
                        required=False, type=valid_date)
    parser.add_mutually_exclusive_group(required=False)
    parser.add_argument('--predict', dest='predict_mode', action='store_true')
    parser.add_argument('--train', dest='predict_mode', action='store_false')
    parser.set_defaults(predict_mode=False)
    parser.add_argument('--rundir', dest='run_dir',
                        help="run directory is in the format: run_YYYYMMDD_hhmmss",
                        required=False)
    args = parser.parse_args()

    # Logging

    if args.debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logging.basicConfig(format="[%(asctime)s] %(levelname)s\t%(message)s",
                        filename="market_flow.log", filemode='a', level=log_level,
                        datefmt='%m/%d/%y %H:%M:%S')
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s\t%(message)s",
                                  datefmt='%m/%d/%y %H:%M:%S')
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    console.setLevel(logging.INFO)
    logging.getLogger().addHandler(console)

    # Start the pipeline

    logger.info('*'*80)
    logger.info("MarketFlow Start")
    logger.info('*'*80)

    # Set train and predict dates

    if args.train_date:
        train_date = args.train_date
    else:
        train_date = datetime.datetime(1900, 1, 1).strftime("%Y-%m-%d")

    if args.predict_date:
        predict_date = args.predict_date
    else:
        predict_date = datetime.date.today().strftime("%Y-%m-%d")

    # Verify that the dates are in sequence.

    if train_date >= predict_date:
        raise ValueError("Training date must be before prediction date")
    else:
        logger.info("Training Date: %s", train_date)
        logger.info("Prediction Date: %s", predict_date)

    # Read model configuration file

    _, model_specs = get_model_config()
    model_specs['predict_mode'] = args.predict_mode
    model_specs['predict_date'] = predict_date
    model_specs['train_date'] = train_date

    # Read AlphaPy root directory

    alphapy_root = os.environ.get('ALPHAPY_ROOT')
    if not alphapy_root:
        root_error_string = "ALPHAPY_ROOT environment variable must be set"
        logger.info(root_error_string)
        sys.exit(root_error_string)
    else:
        model_specs['alphapy_root'] = alphapy_root

    # Read AlphaPy configuration file
    alphapy_specs = get_alphapy_config(alphapy_root)

    # Read market configuration file
    _, market_specs = get_market_config()

    # If not in prediction mode, then create the training infrastructure.

    if not model_specs['predict_mode']:
        # create the directory infrastructure if necessary
        output_dirs = ['config', 'runs']
        for od in output_dirs:
            output_dir = SSEP.join([model_specs['directory'], od])
            if not os.path.exists(output_dir):
                logger.info("Creating directory %s", output_dir)
                os.makedirs(output_dir)
        # create the run directory
        dt_stamp = datetime_stamp()
        run_dir_name = USEP.join(['run', dt_stamp])
        run_dir = SSEP.join([model_specs['directory'], 'runs', run_dir_name])
        os.makedirs(run_dir)
        # create the subdirectories of the runs directory
        sub_dirs = ['config', 'input', 'model', 'output', 'plots', 'systems']
        for sd in sub_dirs:
            output_dir = SSEP.join([run_dir, sd])
            if not os.path.exists(output_dir):
                logger.info("Creating directory %s", output_dir)
                os.makedirs(output_dir)
        # copy the market file to the config directory
        file_names = ['model.yml', 'market.yml']
        for file_name in file_names:
            src_file = SSEP.join([model_specs['directory'], 'config', file_name])
            dst_file = SSEP.join([run_dir, 'config', file_name])
            shutil.copyfile(src_file, dst_file)
    else:
        run_dir = args.run_dir if args.run_dir else None
        if not run_dir:
            # get latest directory
            search_dir = SSEP.join([model_specs['directory'], 'runs'])
            run_dir = most_recent_file(search_dir, 'run_*')
    model_specs['run_dir'] = run_dir

    # Create a model object from the specifications
    model = Model(model_specs)

    # Start the pipeline
    model = market_pipeline(alphapy_specs, model, market_specs)

    # Complete the pipeline

    logger.info('*'*80)
    logger.info("MarketFlow End")
    logger.info('*'*80)


#
# MAIN PROGRAM
#

if __name__ == "__main__":
    main()
