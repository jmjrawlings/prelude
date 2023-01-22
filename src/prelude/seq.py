from typing import TypeVar, Sequence, Tuple, Generator, Union, Literal
from pandas import DataFrame, Series
from .log import get_logger

log = get_logger(__name__)


T = TypeVar("T")


Method = Union[Literal['keys'], Literal['values']]
    

def iter(*args, field='', method: Method = 'keys') -> Generator:
    """
    Iterate over the given arguments

    args:
        Argument to iterate over    
    field: Optional[str]
        If given, dataframes and dicts will have this field extracted
    strict: bool
        If strict, dataframes passed in much have the
        column specified under 'field'
    method: Union['keys', 'values']
    eg:
        iterate(1, 2, 3, [4,5,6]) == [1,2,3,4,5,6]
        iterate(pd.Series(), set([1,2,3]), 1,2,3, unique=True) = [1,2,3]
        iterate(..dataframes, field='name', sort=True) == [1,2,3,4,.....]
        iterate(False) == [False]
        iterate([1,2],None, allow_none=True) == [1, 2, None]
    """
    
    iterkeys = method == 'keys'
    
    def recurse(arg):
        t = type(arg)
        n = t.__name__
        log.debug(f'iter {n} = {arg}')

        # Pandas DataFrames
        if isinstance(arg, DataFrame):
            if not field:
                if iterkeys:
                    yield from recurse(arg.index)
            elif field in arg.columns:
                yield from recurse(arg[field])
            elif arg.index.name == field:
                yield from recurse(arg.index)

        # Pandas Series
        elif isinstance(arg, Series):
            if not field:
                if iterkeys:
                    yield from recurse(arg.index)
                else:
                    yield from recurse(arg.values)
            elif arg.index.name == field:
                yield from recurse(arg.index)
            elif iterkeys:
                yield from recurse(arg.index)
            else:
                yield from recurse(arg.values)

        # Dictionary
        elif isinstance(arg, dict):
            
            if field and field in arg:
                yield from recurse(arg[field])
            elif iterkeys:
                for key in arg.keys():
                    yield from recurse(key)
            else:
                for val in arg.values():
                    yield from recurse(val)
            
        # Iterable
        elif hasattr(arg, '__iter__') and not isinstance(arg, str):
            for item in arg:
                yield from recurse(item)

        # Has the specific field
        elif hasattr(arg, field):
            yield from recurse(getattr(arg, field))

        # Must be a value
        else:
            log.debug('iterate %s', arg)
            yield arg
    

    yield from recurse(args)



def enumerate1(seq: Sequence[T]) -> Generator[Tuple[int, T], None, None]:
    """
    Enumerate the sequence starting
    from 1
    """
    for i,x in enumerate(seq):
        yield i+1, x


def pairwise(seq: Sequence[T]) -> Generator[Tuple[T,T], None, None]:
  """
  Iterate over the given sequence in a pairwise
  fashion
  """
  from itertools import tee, zip_longest
  a,b = tee(seq, 2)
  
  try:
    next(b)
  except StopIteration:
    return
    yield

  for i,j in zip(a,b):
    yield i,j