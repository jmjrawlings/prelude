from typing import Tuple, Set
from pandas import DataFrame, Series
from warnings import warn


def to_set(*args, sort=False, field='', map=None, raise_if_empty=False, debug=False, strict=False, null_values={None}) -> Set:
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
  
  def handle(arg, map=map):
    """
    Handle a single argument
    """
    
    if debug:
      print(f'to-set: {type(arg)}')

    if arg in null_values:
      pass
    
    # Argument is a Dataframe 
    elif isinstance(arg, DataFrame):
      
      # Dataframe contains desired column
      if field and (field in arg.columns):
        handle(arg[field])
      # Dataframe index is desired column
      elif field and (arg.index.name == field):
        handle(arg.index)
      # No field specified - use index
      elif not field:
        handle(arg.index)
      # Field given but not found
      elif strict:
        raise ValueError(f'Could not extract field "{field}" from dataframe.')
      else:
        warn(f'Could not extract field "{field}" from dataframe.')
        pass

    # Argument is a Series
    elif isinstance(arg, Series):
      # Series name matches field
      if field and (arg.name == field):
        handle(arg.values)
      # Series index matches field
      elif field and (arg.index.name == field):
        handle(arg.index)
      elif strict:
        raise ValueError(f'Neither series name or index where called "{field}"')
      else:
        warn(f'Neither series name or index has the name "{field}"')
        handle(arg.values)
        
    # Argument is an Iterable
    elif hasattr(arg, '__iter__') and not isinstance(arg, str):
      for item in arg:
        handle(item)
      
    # A mapping function was given
    elif map is not None:
      handle(map(arg), map=None)

    # Must be a value
    else:
      items.add(arg)

  handle(args)
      
  if sort:
    items = set(sorted(items))
    
  if (not items) and raise_if_empty:
    raise ValueError(f'The set was empty')
    
  return items

def to_sorted_set(*args, **kwargs):
  return to_set(*args, sort=True, **kwargs)

def venn_diagram(a, b) -> Tuple[Set, Set, Set]:
  """
  Returns the venn diagram of the left and
  right sets, ie:
  - The elements in a only
  - The elements in both a and b
  - The elements in b only
  """
  set_a = to_set(a)
  set_b = to_set(b)
    
  common = set_a.intersection(set_b)
  a_only = set_a.difference(common)
  b_only = set_b.difference(common)
  return a_only, common, b_only