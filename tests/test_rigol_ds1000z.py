from pytest import fixture

from rigol_ds1000z import Rigol_DS1000Z


@fixture(scope="function")
def oscope():
    with Rigol_DS1000Z() as oscope:
        oscope.ieee(rst=True)
        yield oscope


def test_write_read_query(oscope):
    idn = "RIGOL TECHNOLOGIES,DS1104Z,DS1ZA224812889,00.04.04.SP4"
    oscope.write("*IDN?")
    assert oscope.read() == idn
    assert oscope.query("*IDN?", delay=1) == idn


def test_big_buttons(oscope):
    oscope.stop()
    oscope.clear()
    oscope.run()
    oscope.autoscale()
    oscope.single()
    oscope.tforce()
