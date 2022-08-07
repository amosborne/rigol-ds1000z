from random import randint

from pytest import approx, fixture

from rigol_ds1000z import Rigol_DS1000Z


@fixture(scope="function")
def oscope():
    with Rigol_DS1000Z() as oscope:
        oscope.ieee(rst=True)
        yield oscope


def test_bwlimit(oscope):
    n = randint(1, 4)
    assert oscope.channel(n, bwlimit=True).bwlimit
    assert not oscope.channel(n, bwlimit=False).bwlimit


def test_coupling(oscope):
    n = randint(1, 4)
    for coupling in ["AC", "DC", "GND"]:
        assert oscope.channel(n, coupling=coupling).coupling == coupling


def test_display(oscope):
    n = randint(1, 4)
    assert oscope.channel(n, display=True).display
    assert not oscope.channel(n, display=False).display


def test_invert(oscope):
    n = randint(1, 4)
    assert oscope.channel(n, invert=True).invert
    assert not oscope.channel(n, invert=False).invert


def test_units(oscope):
    n = randint(1, 4)
    for units in ["VOLT", "WATT", "AMP", "UNKN"]:
        assert oscope.channel(n, units=units).units == units


def test_tcal(oscope):
    n = randint(1, 4)
    assert oscope.channel(n, tcal=n * 20e-9).tcal == approx(n * 20e-9, 1e-12)


def test_vertical_byscale(oscope):
    n = randint(1, 4)
    channel = oscope.channel(n, vernier=False, probe=10, offset=-1.5, scale=0.5)
    assert not channel.vernier
    assert channel.probe == 10
    assert channel.offset == -1.5
    assert channel.scale == 0.5
    assert channel.range == 4


def test_vertical_byrange(oscope):
    n = randint(1, 4)
    channel = oscope.channel(n, vernier=True, probe=1, offset=0, range=6)
    assert channel.vernier
    assert channel.probe == 1
    assert channel.offset == 0
    assert channel.scale == 0.75
    assert channel.range == 6
