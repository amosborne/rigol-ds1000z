from collections import namedtuple
from typing import Optional

CHANNEL = namedtuple(
    "CHANNEL",
    "bwlimit coupling display invert offset range tcal scale probe units vernier",
)


def channel(
    oscope,
    n: int,
    bwlimit: Optional[bool] = None,
    coupling: Optional[str] = None,
    display: Optional[bool] = None,
    invert: Optional[bool] = None,
    offset: Optional[float] = None,
    range: Optional[float] = None,
    tcal: Optional[float] = None,
    scale: Optional[float] = None,
    probe: Optional[float] = None,
    units: Optional[str] = None,
    vernier: Optional[bool] = None,
):
    root = ":CHAN{:d}:".format(n)

    if bwlimit is not None:
        cmd = "20M" if bwlimit else "OFF"
        oscope.write(root + "BWL " + cmd)

    if coupling is not None:
        oscope.write(root + "COUP " + coupling)

    if display is not None:
        oscope.write(root + "DISP {:d}".format(display))

    if invert is not None:
        oscope.write(root + "INV {:d}".format(invert))

    if vernier is not None:
        oscope.write(root + "VERN {:d}".format(vernier))

    if probe is not None:
        oscope.write(root + "PROB {:0.2f}".format(probe))

    if range is not None:
        oscope.write(root + "RANG {:0.10f}".format(range))

    if scale is not None:
        oscope.write(root + "SCAL {:0.10f}".format(scale))

    if offset is not None:
        oscope.write(root + "OFFS {:0.10f}".format(offset))

    if tcal is not None:
        oscope.write(root + "TCAL {:0.10f}".format(tcal))

    if units is not None:
        oscope.write(root + "UNIT " + units)

    return CHANNEL(
        bwlimit=oscope.query(root + "BWL?") == "20M",
        coupling=oscope.query(root + "COUP?"),
        display=bool(int(oscope.query(root + "DISP?"))),
        invert=bool(int(oscope.query(root + "INV?"))),
        vernier=bool(int(oscope.query(root + "VERN?"))),
        probe=float(oscope.query(root + "PROB?")),
        offset=float(oscope.query(root + "OFFS?")),
        range=float(oscope.query(root + "RANG?")),
        scale=float(oscope.query(root + "SCAL?")),
        tcal=float(oscope.query(root + "TCAL?")),
        units=oscope.query(root + "UNIT?"),
    )
