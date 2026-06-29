from collections import namedtuple
from typing import TYPE_CHECKING, Optional, Union

from rigol_ds1000z.src._scpi import (
    Binary,
    Float,
    Int,
    String,
    read_fields,
    write_fields,
)

if TYPE_CHECKING:
    from rigol_ds1000z.src.oscope import Rigol_DS1000Z

DISPLAY = namedtuple("DISPLAY", "type grading_time wbrightness grid gbrightness data")

_SETTABLE = (
    String("type", ":DISP:TYPE"),
    Float("grading_time", ":DISP:GRAD:TIME", keywords=("MIN", "INF")),
    Int("wbrightness", ":DISP:WBR"),
    String("grid", ":DISP:GRID"),
    Int("gbrightness", ":DISP:GBR"),
)

# read-only fields (queried, never written)
_READONLY = (Binary("data", ":DISP:DATA"),)


def display(
    oscope: "Rigol_DS1000Z",
    type: Optional[str] = None,
    grading_time: Union[str, float, None] = None,
    wbrightness: Optional[int] = None,
    grid: Optional[str] = None,
    gbrightness: Optional[int] = None,
):
    """
    Send commands to control an oscilloscope's display. All arguments are optional.

    Args:
        type (str): ``:DISPlay:TYPE``
        grading_time (str, float): ``:DISPlay:GRADing:TIME``
        wbrightness (int): ``:DISPlay:WBRightness``
        grid (str): ``:DISPlay:GRID``
        gbrightness: ``:DISPlay:GBRightness``

    Returns:
        A namedtuple with a field for each argument, queried back regardless of
        which were provided, plus the read-only ``data`` screen capture
        (``:DISPlay:DATA?``).
    """
    provided = dict(
        type=type,
        grading_time=grading_time,
        wbrightness=wbrightness,
        grid=grid,
        gbrightness=gbrightness,
    )
    write_fields(oscope, _SETTABLE, provided)
    return DISPLAY(**read_fields(oscope, _SETTABLE + _READONLY))
