from random import randint


def test_big_buttons(oscope):
    oscope.stop()
    oscope.clear()
    oscope.run()
    oscope.autoscale()
    oscope.single()
    oscope.tforce()


def test_idn(oscope):
    assert oscope.idn() == "RIGOL TECHNOLOGIES,DS1104Z,DS1ZA224812889,00.04.04.SP4"


def test_status_byte(oscope):
    oscope.cls()
    sre = 2 ** randint(2, 5)
    assert oscope.sre(sre) == sre
    assert oscope.stb() == 0


def test_standard_event(oscope):
    oscope.cls()
    ese = 2 ** randint(2, 5)
    assert oscope.ese(ese) == ese
    assert oscope.esr() == 0
