from typing import Tuple, Set
from pandas import DataFrame, Series
from warnings import warn
from .seq_utils import iterate


def make(*args, field='', method='keys'):
    """
    Convert the given argument to a set.

    args: Any
    The items of the set
    sort: bool
    If true, returned set will be sorted
    map: Optional[Callable]
    If exists, function will be applied to the elements
    field: Optional[str]
    If given, dataframes will have this field extracted
    error_if_empty: bool
    If true, an error is thrown if the resulting list is empty
    debug: bool
    If true, debugging information is printed
    strict: bool
    If strict, dataframes passed in much have the
    column specified under 'field'
    raise_if_empty: bool
    If true, an exception will be raised if the
    resulting list is empty

    eg:
    to_list(1, 2, 3, [4,5,6]) == [1,2,3,4,5,6]
    to_list(pd.Series(), set([1,2,3]), 1,2,3, unique=True) = [1,2,3]
    to_list(..dataframes, field=TRV_ID, sort=True) == [1,2,3,4,.....]
    to_list(False) == [False]
    to_list([1,2],None, allow_none=True) == [1, 2, None]
    """

    items = set()
    for item in iterate(*args, field=field, method=method):
        items.add(item)

    return items


def sorted(*args, **kwargs):
    """
    Create a sorted set from the given arguments
    """        
    return set(sorted(make(*args, **kwargs)))
 

def venn(a, b) -> Tuple[Set, Set, Set]:
    """
    Returns the venn diagram of the left and
    right sets, ie:
    - The elements in a only
    - The elements in both a and b
    - The elements in b only
    """
    set_a = make(a)
    set_b = make(b)

    common = set_a.intersection(set_b)
    a_only = set_a.difference(common)
    b_only = set_b.difference(common)
    return a_only, common, b_only