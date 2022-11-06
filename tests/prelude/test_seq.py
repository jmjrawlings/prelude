from src.prelude import *


def test_pairwise():
    for i,j in seq.pairwise([1,2,3]):
        assert i + 1 == j

    