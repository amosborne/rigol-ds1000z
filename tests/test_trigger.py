from time import sleep

from pytest import approx


def test_sweep(oscope):
    oscope.autoscale()

    assert oscope.trigger(sweep="AUTO").sweep == "AUTO"
    assert oscope.trigger().status == "TD"

    assert oscope.trigger(sweep="NORM").sweep == "NORM"
    assert oscope.trigger().status == "TD"

    assert oscope.trigger(sweep="SING").sweep == "SING"
    sleep(1)  # let the single acquisition capture and settle to STOP
    assert oscope.trigger().status == "STOP"


def test_noisereject(oscope):
    assert oscope.trigger(nreject=True).nreject
    assert not oscope.trigger(nreject=False).nreject


def test_trigger_edge(oscope):
    oscope.autoscale()

    trigger = oscope.trigger(
        mode="EDGE",
        holdoff=1e-6,
        coupling="DC",
        edge_source=2,
        edge_slope="NEG",
        edge_level=0.5,
    )

    assert trigger.mode == "EDGE"
    assert trigger.holdoff == 1e-6
    assert trigger.coupling == "DC"
    assert trigger.edge_source == 2
    assert trigger.edge_slope == "NEG"
    assert trigger.edge_level == 0.5


def test_trigger_pulse(oscope):
    oscope.autoscale()

    trigger = oscope.trigger(
        mode="PULS",
        pulse_source=2,
        pulse_when="PGR",
        pulse_level=0.5,
        pulse_lwidth=1e-6,
    )

    assert trigger.mode == "PULS"
    assert trigger.pulse_source == 2
    assert trigger.pulse_when == "PGR"
    assert trigger.pulse_level == 0.5
    assert trigger.pulse_lwidth == approx(1e-6)


def test_trigger_slope(oscope):
    oscope.autoscale()

    trigger = oscope.trigger(
        mode="SLOP",
        slope_source=2,
        slope_when="PGR",
        slope_tlower=1e-6,
        slope_alevel=1.0,
        slope_blevel=0.0,
    )

    assert trigger.mode == "SLOP"
    assert trigger.slope_source == 2
    assert trigger.slope_when == "PGR"
    assert trigger.slope_tlower == approx(1e-6)
    assert trigger.slope_alevel == 1.0
    assert trigger.slope_blevel == 0.0
