from src.prelude.set_utils import *

def test_to_set():
  assert to_set(1,2,{1,2,3},[3,2,1]) == {1,2,3}
  assert to_set({3},{2},{10},1,[2,3,4], sort=True) == {1,2,3,4,10}


def test_venn_diagram():
  left,middle,right = venn_diagram([1,1,1,1,1],[22,3,3,2,3,2])
  assert left == {1}
  assert middle == set()
  assert right == {22,3,2}
  
  left,mid,right = venn_diagram(['a','b','c'],['c','d','a'])
  assert left == {'b'}
  assert mid == {'a','c'}
  assert right == {'d'}  