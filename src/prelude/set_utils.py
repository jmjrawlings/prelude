from typing import Tuple, Set, List  


def to_set(*args, **kwargs):
  return set(to_list(*args, unique=False, **kwargs))

def to_sorted_set(*args, **kwargs):
  return set(to_list(*args, sort=True, unique=False, **kwargs))

def pairwise(xs : List):
  """
  Iterate over the given list in a pairwise
  fashion
  """
  for a,b in zip(xs[:-1], xs[1:]):
    yield a,b
   

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