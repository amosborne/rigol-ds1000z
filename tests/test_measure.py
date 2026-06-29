from time import sleep

from pytest import approx


def test_source(oscope):
    assert oscope.measure(source=2).source == 2
    assert oscope.measure(source="MATH").source == "MATH"


def test_item(oscope):
    oscope.autoscale()
    # calibration square wave ~3 Vpp
    assert oscope.measure(source=2, item="VPP").item == approx(3.0, rel=0.2)


def test_frequency(oscope):
    oscope.autoscale()
    assert oscope.measure(source=2, item="FREQ").item == approx(1e3, rel=0.2)


def test_counter(oscope):
    oscope.autoscale()
    oscope.measure(counter_source=2)
    sleep(1)  # let the counter gate before reading its value
    assert oscope.measure().counter_value == approx(1e3, rel=0.2)
    assert oscope.measure(counter_source="OFF").counter_value == 0


def test_statistics(oscope):
    oscope.autoscale()
    measure = oscope.measure(
        source=2,
        statistic_item=("CURR", "VPP"),
        statistic_mode="EXTR",
        statistic_display=True,
    )
    assert measure.statistic_mode == "EXTR"
    assert measure.statistic_item == approx(3.0, rel=0.2)
