from pytest import approx


def test_bwlimit(oscope, n):
    assert oscope.channel(n, bwlimit=True).bwlimit
    assert not oscope.channel(n, bwlimit=False).bwlimit


def test_coupling(oscope, n):
    for coupling in ["AC", "DC", "GND"]:
        assert oscope.channel(n, coupling=coupling).coupling == coupling


def test_display(oscope, n):
    assert oscope.channel(n, display=True).display
    assert not oscope.channel(n, display=False).display


def test_invert(oscope, n):
    assert oscope.channel(n, invert=True).invert
    assert not oscope.channel(n, invert=False).invert


def test_units(oscope, n):
    for units in ["VOLT", "WATT", "AMP", "UNKN"]:
        assert oscope.channel(n, units=units).units == units


def test_tcal(oscope, n):
    assert oscope.channel(n, tcal=n * 20e-9).tcal == approx(n * 20e-9, 1e-12)


def test_vertical_byscale(oscope, n):
    channel = oscope.channel(n, vernier=False, probe=10, offset=-1.5, scale=0.5)
    assert not channel.vernier
    assert channel.probe == 10
    assert channel.offset == -1.5
    assert channel.scale == 0.5
    assert channel.range == 4


def test_vertical_byrange(oscope, n):
    channel = oscope.channel(n, vernier=True, probe=1, offset=0, range=6)
    assert channel.vernier
    assert channel.probe == 1
    assert channel.offset == 0
    assert channel.scale == 0.75
    assert channel.range == 6
