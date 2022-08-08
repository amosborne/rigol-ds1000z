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
    """
    Send IEEE488.2 common commands. All arguments are optional.
    The device reset command is followed by a 5 seceond delay.

    Args:
        cls (bool): ``*CLS``
        ese (int): ``*ESE``
        esr (bool): ``*ESR?``
        opc (bool): ``*OPC``
        rst (bool): ``*RST``
        sre (int): ``*SRE``
        stb (bool): ``*STB?``
        tst (bool): ``*TST?``

    Returns:
        A namedtuple with fields corresponding to the named arguments of this function (except ``cls`` and ``rst``).
        All fields are queried regardless of which arguments were initially provided.
        The ``idn`` field is additionally provided as a result of the query ``*IDN?``.
    """
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
