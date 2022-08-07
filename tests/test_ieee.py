from random import randint

from pytest import fixture

from rigol_ds1000z import Rigol_DS1000Z


@fixture(scope="function")
def oscope():
    with Rigol_DS1000Z() as oscope:
        oscope.ieee(rst=True)
        yield oscope


def test_idn(oscope):
    assert oscope.ieee().idn == "RIGOL TECHNOLOGIES,DS1104Z,DS1ZA224812889,00.04.04.SP4"


def test_opc(oscope):
    assert oscope.ieee(opc=True).opc


def test_status_byte(oscope):
    sre = 2 ** randint(2, 5)
    assert oscope.ieee(cls=True, sre=sre).sre == sre
    assert oscope.ieee(stb=True).stb == 0


def test_standard_event(oscope):
    ese = 2 ** randint(2, 5)
    assert oscope.ieee(cls=True, ese=ese).ese == ese
    assert oscope.ieee(esr=True).esr == 0
