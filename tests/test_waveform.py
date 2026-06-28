from time import sleep


def test_mode(oscope):
    for mode in ["NORM", "MAX", "RAW"]:
        assert oscope.waveform(mode=mode).mode == mode


def test_format(oscope):
    for format in ["WORD", "BYTE", "ASC"]:
        assert oscope.waveform(format=format).format == format


def test_source(oscope, n):
    assert oscope.waveform(source="MATH").source == "MATH"
    assert oscope.waveform(source=n).source == n


def test_start_stop(oscope):
    waveform = oscope.waveform(start=2, stop=3)
    assert waveform.start == 2
    assert waveform.stop == 3


def test_preamble(oscope):
    oscope.autoscale()
    oscope.single()
    sleep(1)  # let the single acquisition capture a complete frame before reading
    waveform = oscope.waveform(format="BYTE")
    assert waveform.points == waveform.stop - waveform.start + 1
    assert waveform.count >= 1
    assert waveform.xincrement > 0
    assert waveform.yincrement > 0
    assert len(waveform.data) == waveform.points
