from collections import namedtuple
from typing import TYPE_CHECKING, Optional

from rigol_ds1000z.src._scpi import Bool, Float, String, read_fields, write_fields

if TYPE_CHECKING:
    from rigol_ds1000z.src.oscope import Rigol_DS1000Z

CHANNEL = namedtuple(
    "CHANNEL",
    "bwlimit coupling display invert vernier probe range scale offset tcal units",
)

# Declaration order is the write order. ``range``, ``scale``, and ``offset`` are
# potentially conflicting and are deliberately issued in that order.
_SETTABLE = (
    Bool("bwlimit", ":CHAN{n}:BWL", true="20M", false="OFF"),
    String("coupling", ":CHAN{n}:COUP"),
    Bool("display", ":CHAN{n}:DISP"),
    Bool("invert", ":CHAN{n}:INV"),
    Bool("vernier", ":CHAN{n}:VERN"),
    Float("probe", ":CHAN{n}:PROB"),
    Float("range", ":CHAN{n}:RANG"),
    Float("scale", ":CHAN{n}:SCAL"),
    Float("offset", ":CHAN{n}:OFFS"),
    Float("tcal", ":CHAN{n}:TCAL"),
    String("units", ":CHAN{n}:UNIT"),
)


def channel(
    oscope: "Rigol_DS1000Z",
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
    """
    Send commands to control an oscilloscope's vertical channel.
    Other than the channel number, all arguments are optional.
    ``range``, ``scale``, and ``offset`` are potentially conflicting
    commands if all three are simultaneously specified; they are issued in that order.

    Args:
        n (int): The channel to be controlled (1 through 4).
        bwlimit (bool): ``:CHANnel<n>:BWLimit``
        coupling (str): ``:CHANnel<n>:COUPling``
        display (bool): ``:CHANnel<n>:DISPlay``
        invert (bool): ``:CHANnel<n>:INVert``
        offset (float): ``:CHANnel<n>:OFFSet``
        range (float): ``:CHANnel<n>:RANGe``
        tcal (float): ``:CHANnel<n>:TCAL``
        scale (float): ``:CHANnel<n>:SCALe``
        probe (float): ``:CHANnel<n>:PROBe``
        units (str): ``:CHANnel<n>:UNITs``
        vernier (bool): ``:CHANnel<n>:VERNier``

    Returns:
        A namedtuple with a field for each argument, queried back regardless of
        which were provided.
    """
    provided = dict(
        bwlimit=bwlimit,
        coupling=coupling,
        display=display,
        invert=invert,
        vernier=vernier,
        probe=probe,
        range=range,
        scale=scale,
        offset=offset,
        tcal=tcal,
        units=units,
    )
    write_fields(oscope, _SETTABLE, provided, n=n)
    return CHANNEL(**read_fields(oscope, _SETTABLE, n=n))
