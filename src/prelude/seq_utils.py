from typing import TypeVar, Sequence, Tuple, Generator

T = TypeVar("T")


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

  for i,j in zip_longest(a,b):
    yield i,j