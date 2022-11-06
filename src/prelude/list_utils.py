"""
List utilities
"""
from typing import List, TypeVar
from . import seq_utils as seq
from . import set_utils as set

T = TypeVar("T")


def make(*args, field='', method='values') -> List:
    """
    Convert the given argument to list.

    args: Any
    The items of the list
    field: str
    If given, dataframes will have this field extracted

    eg:
    to_list(1, 2, 3, [4,5,6]) == [1,2,3,4,5,6]
    to_list(pd.Series(), set([1,2,3]), 1,2,3, unique=True) = [1,2,3]
    to_list(..dataframes, field=TRV_ID, sort=True) == [1,2,3,4,.....]
    to_list(False) == [False]
    to_list([1,2],None, allow_none=True) == [1, 2, None]
    """
    items = list(seq.iterate(*args, field=field, method=method))
    return items


def distinct(*args, **kwargs):
    return list(set.make(*args, **kwargs))

def unique(*args, **kwargs):
    return distinct(*args, **kwargs)    

def sort(*args, **kwargs):
    return sorted(make(*args, **kwargs))
