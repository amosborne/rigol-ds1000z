import os

from rigol_ds1000z import Rigol_DS1000Z, process_display, process_waveform


def test_process_display():
    with Rigol_DS1000Z() as oscope:
        oscope.autoscale()
        filename = "tests/test_process_display_data.png"
        process_display(oscope.display(), filename=filename)
        assert os.path.isfile(filename)
        os.remove(filename)


def test_process_waveform():
    with Rigol_DS1000Z() as oscope:
        oscope.autoscale()
        filename = "tests/test_process_waveform.csv"
        process_waveform(oscope.waveform(source=2), filename=filename)
        assert os.path.isfile(filename)
        os.remove(filename)
