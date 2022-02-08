import os
import subprocess

from rigol_ds1000z import Rigol_DS1000Z, find_visa, process_display, process_waveform


def test_find_visa():
    assert find_visa() == "USB0::0x1AB1::0x04CE::DS1ZA224812889::INSTR"


def test_process_display():
    with Rigol_DS1000Z(find_visa()) as oscope:
        oscope.autoscale()
        filename = "tests/test_process_display_data.png"
        process_display(oscope.display(), filename=filename)
        assert os.path.isfile(filename)
        os.remove(filename)


def test_process_waveform():
    with Rigol_DS1000Z(find_visa()) as oscope:
        oscope.autoscale()
        filename = "tests/test_process_waveform.csv"
        process_waveform(oscope.waveform(source=2), filename=filename)
        assert os.path.isfile(filename)
        os.remove(filename)


def test_cli():
    subprocess.call(
        ["rigol-ds1000z", "-d", "tests/test_cli.png", "-w", "2", "tests/test_cli.csv"],
        shell=True,
    )
    assert os.path.isfile("tests/test_cli.png")
    os.remove("tests/test_cli.png")
    assert os.path.isfile("tests/test_cli.csv")
    os.remove("tests/test_cli.csv")
