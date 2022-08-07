from pytest import fixture

from rigol_ds1000z import Rigol_DS1000Z


@fixture(scope="function")
def oscope():
    with Rigol_DS1000Z() as oscope:
        oscope.ieee(rst=True)
        yield oscope


def test_mode(oscope):
    for mode in ["MAIN", "XY", "ROLL"]:
        assert oscope.timebase(mode=mode).mode == mode


def test_main(oscope):
    timebase = oscope.timebase(main_scale=1e-3, main_offset=-1e-3)
    assert timebase.main_scale == 1e-3
    assert timebase.main_offset == -1e-3


def test_delay(oscope):
    timebase = oscope.timebase(
        main_scale=10e-6,
        main_offset=0,
        delay_scale=2e-6,
        delay_offset=1e-6,
        delay_enable=True,
    )
    assert timebase.main_scale == 10e-6
    assert timebase.main_offset == 0
    assert timebase.delay_scale == 2e-6
    assert timebase.delay_offset == 1e-6
    assert timebase.delay_enable
    assert not oscope.timebase(delay_enable=False).delay_enable
