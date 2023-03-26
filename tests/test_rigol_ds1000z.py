from random import randint

from pytest import fixture

from rigol_ds1000z import Rigol_DS1000Z


@fixture(scope="function")
def oscope():
    with Rigol_DS1000Z() as oscope:
        oscope.rst()
        yield oscope


def test_write_read_query(oscope):
    idn = "RIGOL TECHNOLOGIES,DS1104Z,DS1ZA224812889,00.04.04.SP4"
    oscope.write("*IDN?")
    assert oscope.read() == idn
    assert oscope.idn() == idn


def test_big_buttons(oscope):
    oscope.stop()
    oscope.clear()
    oscope.run()
    oscope.autoscale()
    oscope.single()
    oscope.tforce()


def test_ieee(oscope):
    val = 2 ** randint(2, 5)

    oscope.cls()
    assert oscope.ese(val) == val
    assert oscope.esr() == 0

    oscope.cls()
    assert oscope.sre(val) == val
    assert oscope.stb() == 0
