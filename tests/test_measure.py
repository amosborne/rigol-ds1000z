from pytest import approx, fixture

from rigol_ds1000z import Rigol_DS1000Z


@fixture(scope="function")
def oscope():
    with Rigol_DS1000Z() as oscope:
        oscope.ieee(rst=True)
        yield oscope


def test_source(oscope):
    assert oscope.measure(source=2).source == 2
    assert oscope.measure(source="MATH").source == "MATH"


def test_item(oscope):
    oscope.autoscale()

    measure = oscope.measure(source=2, item="VPP")
    assert measure.item == "VPP"
    assert measure.value == approx(3.0, rel=0.2)  # calibration square wave ~3 Vpp


def test_frequency(oscope):
    oscope.autoscale()
    assert oscope.measure(source=2, item="FREQ").value == approx(1e3, rel=0.2)


def test_counter(oscope):
    oscope.autoscale()
    assert oscope.measure(counter=2).counter == approx(1e3, rel=0.2)
    assert oscope.measure(counter="OFF").counter is None


def test_statistics(oscope):
    oscope.autoscale()

    measure = oscope.measure(source=2, item="VPP", statistics=True)
    assert measure.statistics is not None
    assert measure.statistics.current == approx(measure.value, rel=0.2)
