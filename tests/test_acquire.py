def test_type(oscope):
    for type in ["NORM", "AVER", "PEAK", "HRES"]:
        assert oscope.acquire(type=type).type == type


def test_averages(oscope):
    acquire = oscope.acquire(type="AVER", averages=8)
    assert acquire.type == "AVER"
    assert acquire.averages == 8
    assert oscope.acquire(averages=16).averages == 16


def test_memdepth(oscope):
    assert oscope.acquire(memdepth="AUTO").memdepth == "AUTO"


def test_srate(oscope):
    assert oscope.acquire().srate > 0
