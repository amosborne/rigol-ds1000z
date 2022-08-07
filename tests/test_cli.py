import os

VISA = "USB0::0x1AB1::0x04CE::DS1ZA224812889::INSTR"


def test_cli_display_with_visa():
    ret = os.system("rigol-ds1000z -v " + VISA + " -d test.png")
    assert not ret
    assert os.path.isfile("test.png")
    os.remove("test.png")


def test_cli_display_without_visa():
    ret = os.system("rigol-ds1000z -d test.png")
    assert not ret
    assert os.path.isfile("test.png")
    os.remove("test.png")


def test_cli_waveform_with_visa():
    ret = os.system("rigol-ds1000z -v " + VISA + " -w 1 test.csv")
    assert not ret
    assert os.path.isfile("test.csv")
    os.remove("test.csv")


def test_cli_waveform_without_visa():
    ret = os.system("rigol-ds1000z -w 1 test.csv")
    assert not ret
    assert os.path.isfile("test.csv")
    os.remove("test.csv")


def test_cli_display_and_waveform():
    ret = os.system("rigol-ds1000z -d test.png -w 1 test.csv")
    assert not ret
    assert os.path.isfile("test.csv")
    assert os.path.isfile("test.png")
    os.remove("test.csv")
    os.remove("test.png")
