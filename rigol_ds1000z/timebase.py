from collections import namedtuple
from typing import Optional

TIMEBASE = namedtuple(
    "TIMEBASE", "mode main_scale main_offset delay_enable delay_scale delay_offset"
)


def timebase(
    oscope,
    mode: Optional[str] = None,
    main_scale: Optional[float] = None,
    main_offset: Optional[float] = None,
    delay_enable: Optional[bool] = None,
    delay_scale: Optional[float] = None,
    delay_offset: Optional[float] = None,
):
    if mode is not None:
        oscope.write(":TIM:MODE " + mode)

    if main_scale is not None:
        oscope.write(":TIM:SCAL {:0.10f}".format(main_scale))

    if main_offset is not None:
        oscope.write(":TIM:OFFS {:0.10f}".format(main_offset))

    if delay_enable is not None:
        oscope.write(":TIM:DEL:ENAB {:d}".format(delay_enable))

    if delay_scale is not None:
        oscope.write(":TIM:DEL:SCAL {:0.10f}".format(delay_scale))

    if delay_offset is not None:
        oscope.write(":TIM:DEL:OFFS {:0.10f}".format(delay_offset))

    return TIMEBASE(
        mode=oscope.query(":TIM:MODE?"),
        main_scale=float(oscope.query(":TIM:SCAL?")),
        main_offset=float(oscope.query(":TIM:OFFS?")),
        delay_enable=bool(int(oscope.query(":TIM:DEL:ENAB?"))),
        delay_scale=float(oscope.query(":TIM:DEL:SCAL?")),
        delay_offset=float(oscope.query(":TIM:DEL:OFFS?")),
    )
