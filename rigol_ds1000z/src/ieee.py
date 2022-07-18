from collections import namedtuple
from time import sleep
from typing import Optional

IEEE = namedtuple("IEEE", "ese esr idn opc sre stb tst")


def ieee(
    oscope,
    cls: bool = False,
    ese: Optional[int] = None,
    esr: bool = False,
    opc: bool = False,
    rst: bool = False,
    sre: Optional[int] = None,
    stb: bool = False,
    tst: bool = False,
):
    if cls:
        oscope.write("*CLS")

    if ese is not None:
        oscope.write("*ESE {:d}".format(ese))

    if opc:
        oscope.write("*OPC")

    if rst:
        oscope.write("*RST")
        sleep(5)

    if sre is not None:
        oscope.write("*SRE {:d}".format(sre))

    return IEEE(
        ese=int(oscope.query("*ESE?")),
        esr=int(oscope.query("*ESR?")) if esr else None,
        idn=oscope.query("*IDN?"),
        opc=bool(int(oscope.query("*OPC?"))),
        sre=int(oscope.query("*SRE?")),
        stb=int(oscope.query("*STB?")) if stb else None,
        tst=int(oscope.query("*TST?")) if tst else None,
    )
