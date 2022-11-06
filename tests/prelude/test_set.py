from src.prelude import set

def test_make():
  assert set.make(1,2,{1,2,3},[3,2,1]) == {1,2,3}

def test_sorted():  
  assert set.sorted({3},{2},{10},1,[2,3,4]) == {1,2,3,4,10}

def test_venn():
  left,middle,right = set.venn([1,1,1,1,1],[22,3,3,2,3,2])
  assert left == {1}
  assert middle == set.empty()
  assert right == {22,3,2}
  
  left,mid,right = set.venn(['a','b','c'],['c','d','a'])
  assert left == {'b'}
  assert mid == {'a','c'}
  assert right == {'d'}  