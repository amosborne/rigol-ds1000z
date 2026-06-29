from collections import namedtuple
from typing import TYPE_CHECKING, Optional

from rigol_ds1000z.src._scpi import Bool, Float, String, read_fields, write_fields

if TYPE_CHECKING:
    from rigol_ds1000z.src.oscope import Rigol_DS1000Z

TIMEBASE = namedtuple(
    "TIMEBASE", "mode main_scale main_offset delay_enable delay_scale delay_offset"
)

_SETTABLE = (
    String("mode", ":TIM:MODE"),
    Float("main_scale", ":TIM:SCAL"),
    Float("main_offset", ":TIM:OFFS"),
    Bool("delay_enable", ":TIM:DEL:ENAB"),
    Float("delay_scale", ":TIM:DEL:SCAL"),
    Float("delay_offset", ":TIM:DEL:OFFS"),
)


def timebase(
    oscope: "Rigol_DS1000Z",
    mode: Optional[str] = None,
    main_scale: Optional[float] = None,
    main_offset: Optional[float] = None,
    delay_enable: Optional[bool] = None,
    delay_scale: Optional[float] = None,
    delay_offset: Optional[float] = None,
):
    """
    Send commands to control an oscilloscope's horizontal scaling.
    All arguments are optional.

    Args:
        mode (str): ``:TIMebase:MODE``
        main_scale (float): ``:TIMebase:SCALe``
        main_offset (float): ``:TIMebase:OFFSet``
        delay_enable (bool): ``:TIMebase:DELay:ENABle``
        delay_scale (float): ``:TIMebase:DELay:SCALe``
        delay_offset (float): ``:TIMebase:DELay:OFFSet``

    Returns:
        A namedtuple with a field for each argument, queried back regardless of
        which were provided.
    """
    provided = dict(
        mode=mode,
        main_scale=main_scale,
        main_offset=main_offset,
        delay_enable=delay_enable,
        delay_scale=delay_scale,
        delay_offset=delay_offset,
    )
    write_fields(oscope, _SETTABLE, provided)
    return TIMEBASE(**read_fields(oscope, _SETTABLE))
