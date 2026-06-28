from pytest import approx


def test_type(oscope):
    for type in ["NORM", "AVER", "PEAK", "HRES"]:
        assert oscope.acquire(type=type).type == type


def test_averages(oscope):
    acquire = oscope.acquire(type="AVER", averages=8)
    assert acquire.type == "AVER"
    assert acquire.averages == 8
    assert oscope.acquire(averages=16).averages == 16


def test_mdepth(oscope):
    assert oscope.acquire(mdepth=12000).mdepth == 12000
    assert oscope.acquire(mdepth="AUTO").mdepth == "AUTO"


def test_srate(oscope):
    # the acquisition window spans 12 horizontal divisions, so
    # sample rate = memory depth / (timebase scale x 12)
    main_scale = 1e-3
    mdepth = 12000
    oscope.timebase(main_scale=main_scale)
    acquire = oscope.acquire(mdepth=mdepth)
    expected = mdepth / (main_scale * 12)
    assert acquire.srate == approx(expected, rel=1e-3)
