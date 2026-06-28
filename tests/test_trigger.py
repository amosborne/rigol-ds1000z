from pytest import approx, fixture

from rigol_ds1000z import Rigol_DS1000Z


@fixture(scope="function")
def oscope():
    with Rigol_DS1000Z() as oscope:
        oscope.ieee(rst=True)
        yield oscope


def test_sweep(oscope):
    oscope.autoscale()

    assert oscope.trigger(sweep="AUTO").sweep == "AUTO"
    assert oscope.trigger().status == "TD"

    assert oscope.trigger(sweep="NORM").sweep == "NORM"
    assert oscope.trigger().status == "TD"

    assert oscope.trigger(sweep="SING").sweep == "SING"
    assert oscope.trigger().status == "STOP"


def test_noisereject(oscope):
    assert oscope.trigger(noisereject=True).noisereject
    assert not oscope.trigger(noisereject=False).noisereject


def test_trigger_edge(oscope):
    oscope.autoscale()

    trigger = oscope.trigger(
        mode="EDGE", holdoff=1e-6, coupling="DC", source=2, slope="NEG", level=0.5
    )

    assert trigger.mode == "EDGE"
    assert trigger.holdoff == 1e-6
    assert trigger.coupling == "DC"
    assert trigger.source == 2
    assert trigger.slope == "NEG"
    assert trigger.level == 0.5


def test_trigger_pulse(oscope):
    oscope.autoscale()

    trigger = oscope.trigger(mode="PULS", source=2, when="PGR", level=0.5, lower=1e-6)

    assert trigger.mode == "PULS"
    assert trigger.source == 2
    assert trigger.when == "PGR"
    assert trigger.level == 0.5
    assert trigger.lower == approx(1e-6)


def test_trigger_slope(oscope):
    oscope.autoscale()

    trigger = oscope.trigger(
        mode="SLOP", source=2, when="PGR", lower=1e-6, alevel=1.0, blevel=0.0
    )

    assert trigger.mode == "SLOP"
    assert trigger.source == 2
    assert trigger.when == "PGR"
    assert trigger.lower == approx(1e-6)
    assert trigger.alevel == 1.0
    assert trigger.blevel == 0.0
