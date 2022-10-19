from src.prelude import *

def test_times():
    now = dt.now()
    then = now.add(days=100)
    naive = then.naive()
    local = dt.datetime(naive)
    assert local.tz.name == 'UTC'


def test_dates():
    assert dt.today().add(days=1) == dt.tomorrow()
    assert dt.tomorrow().add(days=-2) == dt.yesterday()
