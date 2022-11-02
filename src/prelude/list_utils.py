"""
List utilities
"""


def to_list(*args, unique=False, sort=False, field='', map=None, error_if_empty=False, debug=False, strict=False, allow_none=False):
  """
  Convert the given argument to list.
  
  args: Any
    The items of the list
  unique: bool
    If true, duplicates will be removed from the result
  sort: bool
    If true, returned list will be sorted
  map: Optional[Callable]
    If exists, resulting list elements will be mapped
  field: Optional[str]
    If given, dataframes will have this field extracted
  error_if_empty: bool
    If true, an error is thrown if the resulting list is empty
  debug: bool
    If true, debugging information is printed
  strict: bool
    If strict, dataframes passed in much have the
    column specified under 'field'
    
  eg:
    to_list(1, 2, 3, [4,5,6]) == [1,2,3,4,5,6]
    to_list(pd.Series(), set([1,2,3]), 1,2,3, unique=True) = [1,2,3]
    to_list(..dataframes, field=TRV_ID, sort=True) == [1,2,3,4,.....]
    to_list(False) == [False]
    to_list([1,2],None, allow_none=True) == [1, 2, None]
  """

  items = []
  
  def handle(arg, map=map):
    """
    Handle a single argument
    """
    
    if debug:
      print(f'to-list: {type(arg)}')
      
    if arg is None and not allow_none:
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
      items.append(arg)

  handle(args)
  
  if unique:
    items = list(dict.fromkeys(items))
    
  if sort:
    items = sorted(items)
    
  if (items == []) and error_if_empty:
    raise ValueError(f'The list was empty')
    
  return items

def to_distinct_list(*args, **kwargs):
  return to_list(*args, unique=True, **kwargs)

def to_sorted_list(*args, **kwargs):
  return to_list(*args, sort=True, **kwargs)
  
def to_distinct_sorted_list(*args, **kwargs):
  return to_list(*args, sort=True, unique=True, **kwargs)
