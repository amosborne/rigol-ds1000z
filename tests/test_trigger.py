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
