from src.prelude import *

def test_times():
    now = dt.now()
    then = now.add(days=100)
    paris = then.naive()
    other = dt.datetime(paris)