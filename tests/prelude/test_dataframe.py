from src.prelude import *
from pandas import DataFrame, Series

def test_df_list_keys():
    df = DataFrame(dict(a=[1,2,3]), index=['a','b','c'])
    assert lst.make(df, method='keys') == ['a','b','c']

def test_df_list_vals():
    df = DataFrame(dict(a=[1,2,3]), index=['a','b','c'])
    assert lst.make(df, field='a') == [1,2,3]

def test_series_set():
  assert set.make(Series([1,2,3], index=['a','b','a']), method='values') == {1,2,3}
