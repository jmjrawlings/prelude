from src.prelude.set_utils import *
from src.prelude.list_utils import *
from src.prelude.seq_utils import *


def test_pairwise():
    for i,j in pairwise([1,2,3]):
        assert i + 1 == j

    