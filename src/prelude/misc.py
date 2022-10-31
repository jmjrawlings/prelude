"""
Miscellaneous functions
"""

def show_source_code(function):
  """
  Prints the source code of the 
  given function
  """
  import inspect
  source = inspect.getsource(function)
  for line in source.split('\n'):
    print(line)