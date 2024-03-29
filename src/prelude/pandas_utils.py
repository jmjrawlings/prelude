"""
panda.py

Extensions and helpers for pandas
"""
from . import dt as dt
from typing import Optional, Tuple, Union
import pandas as pd
from pandas import DataFrame, Series
from .lst import *

FrameOrSeries = Union[DataFrame, Series]


def to_timestamp(arg, tz='UTC') -> pd.Timestamp:
  """
  Convert the argument to a pendulum datetime
  to a pandas timestamp
  """
  if isinstance(arg, pd.Timestamp):
    return arg
  elif isinstance(arg, str):
    return pd.Timestamp(arg)
  else:
    time = dt.datetime(arg)
    return pd.Timestamp(time).tz_convert(tz)


def empty(arg) -> bool:
    if isinstance(arg, DataFrame):
        return arg.empty
    elif isinstance(arg, Series):
        return arg.empty
    return bool(arg) 


def non_empty(arg):
    return not empty(arg)    


def shape(arg) -> Tuple[int,int]:
    if arg is None:
        return 0,0
    if isinstance(arg, pd.DataFrame):
        return arg.shape
    elif isinstance(arg, pd.Series):
        return arg.shape
    raise ValueError(f'{type(arg)} was not a DataFrame or Series')


def describe(arg) -> str:
    if arg is None:
        return ''
    else:
        rows, cols = shape(arg)
        return f'{type(arg)} with {rows:,} rows and {cols:,} cols'


def empty_df(df: Optional[DataFrame] = None) -> DataFrame:
  """
  Get an empty version of the
  given dataframe such that
  all column names and index
  name are still intact
  """
  if df is None:
    return DataFrame()
  else:
    assert isinstance(df, pd.DataFrame)
    return df[df.index != df.index]


def rename_columns(df : DataFrame, *args, **kwargs) -> DataFrame:
  """
  rename_columns(df, a=b, c=d, e=f)
  """
  return df.rename(columns=kwargs)


# def describe_time_period(
#     df: DataFrame,
#     start_col = 'start_time',
#     end_col = 'end_time',
#     prefix = '',
#     seconds = False,
#     minutes = True,
#     days = False,
#     duration = False
#     ):
#   periods = df[end_col] - df[start_col]
#   seconds = periods.dt.total_seconds().astype(int)
#   minutes = seconds / 60
#   hours = minutes / 60
  
#   if minutes:  
#     df[prefix_string('minutes')] = minutes_
    
#   if hours:
#     df[prefix_string('hours')] = hours_
    
#   if days:
#     df[prefix_string('days')] = days_
    
#   if duration:
#     # TODO - string description
#     pass

#   return df
  

# def localize_datetime_columns(df: DataFrame, tz=TIMEZONE):
#   for column in df.columns:
#     if df[column].dtype == 'datetime64[ns]':
#       df[column] = df[column].dt.tz_localize(tz)  
  
  
# def filter(df: DataFrame, strict=True, **kwargs) -> DataFrame:
#   """
#   Filter the given dataframe with columns
#   and items provided in kwargs
#   """

#   rows = df.shape[0]
#   for column, arg in kwargs.items():
    
#     if empty(df):
#       print('filter-df: dataframe is empty')
#       return df
    
#     if column not in df.columns:
#       if strict:
#         raise Exception(f'column "{column}" was not found in {to_set(df.columns)}')
#       else:
#         print(f'filter-df: column "{column}" was not found in {to_set(df.columns)}')
#         continue
        
#     items = to_list(arg, unique=True, sort=True, field=column)
#     item_count = len(items)
    
#     match = df[column].isin(items)
#     input_rows = df.shape[0]
#     df = df[match]
#     output_rows = df.shape[0]
#     delta = input_rows - output_rows
#     remaining = output_rows / rows
#     print(f'filter-df: filter "{column}" ({len(items)} items) removed {delta} rows, {output_rows:,} remain ({remaining:.0%})')
    
#   if is_none_or_empty_df(df):
#     print('filter-df: dataframe is empty')
    
#   return df
