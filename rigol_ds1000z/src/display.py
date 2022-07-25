from collections import namedtuple
from typing import Optional, Union

DISPLAY = namedtuple(
    "DISPLAY", "data type grading_time wave_brightness grid grid_brightness"
)


def display(
    oscope,
    clear: bool = False,
    type: Optional[str] = None,
    grading_time: Union[str, float, None] = None,
    wave_brightness: Optional[int] = None,
    grid: Optional[str] = None,
    grid_brightness: Optional[int] = None,
):
    if clear:
        oscope.write(":DISP:CLE")

    if type is not None:
        oscope.write(":DISP:TYPE {:s}".format(type))

    if grading_time is not None:
        if isinstance(grading_time, str):
            oscope.write(":DISP:GRAD:TIME {:s}".format(grading_time))
        else:
            oscope.write(":DISP:GRAD:TIME {:g}".format(grading_time))

    if wave_brightness is not None:
        oscope.write(":DISP:WBR {:d}".format(wave_brightness))

    if grid is not None:
        oscope.write(":DISP:GRID {:s}".format(grid))

    if grid_brightness is not None:
        oscope.write(":DISP:GBR {:d}".format(grid_brightness))

    time = oscope.query(":DISP:GRAD:TIME?")
    if time not in ("MIN", "INF"):
        time = float(time)

    return DISPLAY(
        data=oscope.visa_rsrc.query_binary_values(":DISP:DATA?", "B"),
        type=oscope.query(":DISP:TYPE?"),
        grading_time=time,
        wave_brightness=int(oscope.query(":DISP:WBR?")),
        grid=oscope.query(":DISP:GRID?"),
        grid_brightness=int(oscope.query(":DISP:GBR?")),
    )
