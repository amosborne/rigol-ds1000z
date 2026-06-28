from collections import namedtuple
from typing import Optional, Union

from rigol_ds1000z.src._scpi import Float, Int, String, read_fields, write_fields

DISPLAY = namedtuple("DISPLAY", "data type grading_time wbrightness grid gbrightness")

_FIELDS = (
    String("type", ":DISP:TYPE"),
    Float("grading_time", ":DISP:GRAD:TIME", keywords=("MIN", "INF")),
    Int("wbrightness", ":DISP:WBR"),
    String("grid", ":DISP:GRID"),
    Int("gbrightness", ":DISP:GBR"),
)


def display(
    oscope,
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
        A namedtuple with fields corresponding to the named arguments of this function.
        All fields are queried regardless of which arguments were initially provided.
        The ``data`` field is additionally provided as a result of the query
        ``:DISPlay:DATA?``.
    """
    provided = dict(
        type=type,
        grading_time=grading_time,
        wbrightness=wbrightness,
        grid=grid,
        gbrightness=gbrightness,
    )
    write_fields(oscope, _FIELDS, provided)
    return DISPLAY(
        **read_fields(oscope, _FIELDS),
        data=oscope.visa_rsrc.query_binary_values(":DISP:DATA?", "B"),
    )
