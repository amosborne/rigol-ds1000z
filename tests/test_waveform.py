from random import randint

from pytest import fixture

from rigol_ds1000z import Rigol_DS1000Z


@fixture(scope="function")
def oscope():
    with Rigol_DS1000Z() as oscope:
        oscope.ieee(rst=True)
        yield oscope


def test_mode(oscope):
    for mode in ["NORM", "MAX", "RAW"]:
        assert oscope.waveform(mode=mode).mode == mode


def test_format(oscope):
    for format in ["WORD", "BYTE", "ASC"]:
        assert oscope.waveform(format=format).format == format


def test_source(oscope):
    assert oscope.waveform(source="MATH").source == "MATH"
    n = randint(1, 4)
    assert oscope.waveform(source=n).source == n


def test_start_stop(oscope):
    waveform = oscope.waveform(start=2, stop=3)
    assert waveform.start == 2
    assert waveform.stop == 3


def test_preamble(oscope):
    preamble_format = {0: "BYTE", 1: "WORD", 2: "ASC"}
    preamble_mode = {0: "NORM", 1: "MAX", 2: "RAW"}
    oscope.autoscale()
    waveform = oscope.waveform()
    preamble = waveform.preamble.split(",")
    assert preamble_format[int(preamble[0])] == waveform.format
    assert preamble_mode[int(preamble[1])] == waveform.mode
    assert float(preamble[4]) == waveform.xincrement
    assert float(preamble[5]) == waveform.xorigin
    assert int(preamble[6]) == waveform.xreference
    assert float(preamble[7]) == waveform.yincrement
    assert int(preamble[8]) == waveform.yorigin
    assert int(preamble[9]) == waveform.yreference
