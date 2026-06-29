from collections import namedtuple
from typing import TYPE_CHECKING, Optional, Tuple, Union

from rigol_ds1000z.src._scpi import (
    Bool,
    Float,
    Int,
    Query,
    Source,
    String,
    read_fields,
    write_fields,
)

if TYPE_CHECKING:
    from rigol_ds1000z.src.oscope import Rigol_DS1000Z

MEASURE = namedtuple(
    "MEASURE",
    "source counter_source "
    "setup_max setup_mid setup_min setup_psa setup_psb setup_dsa setup_dsb "
    "statistic_mode statistic_display item statistic_item counter_value",
)


_SETTABLE = (
    Source("source", ":MEAS:SOUR"),
    Source("counter_source", ":MEAS:COUN:SOUR"),
    Int("setup_max", ":MEAS:SET:MAX"),
    Int("setup_mid", ":MEAS:SET:MID"),
    Int("setup_min", ":MEAS:SET:MIN"),
    Source("setup_psa", ":MEAS:SET:PSA"),
    Source("setup_psb", ":MEAS:SET:PSB"),
    Source("setup_dsa", ":MEAS:SET:DSA"),
    Source("setup_dsb", ":MEAS:SET:DSB"),
    String("statistic_mode", ":MEAS:STAT:MODE"),
    Bool("statistic_display", ":MEAS:STAT:DISP"),
    Query("item", ":MEAS:ITEM"),
    Query("statistic_item", ":MEAS:STAT:ITEM"),
)

_READONLY = (Float("counter_value", ":MEAS:COUN:VAL"),)


def measure(
    oscope: "Rigol_DS1000Z",
    item: Optional[str] = None,
    statistic_item: Optional[Tuple[str, str]] = None,
    source: Union[int, str, None] = None,
    counter_source: Union[int, str, None] = None,
    setup_max: Optional[int] = None,
    setup_mid: Optional[int] = None,
    setup_min: Optional[int] = None,
    setup_psa: Union[int, str, None] = None,
    setup_psb: Union[int, str, None] = None,
    setup_dsa: Union[int, str, None] = None,
    setup_dsb: Union[int, str, None] = None,
    statistic_mode: Optional[str] = None,
    statistic_display: Optional[bool] = None,
    statistic_reset: Optional[bool] = None,
    clear: Optional[str] = None,
):
    """
    Send commands to make automatic measurements on an oscilloscope.
    All arguments are optional. The settable fields are written when provided and
    always queried back. The ``item`` argument names an item to measure; the
    returned ``item`` field holds its instantaneous value (``:MEASure:ITEM?``).
    The ``statistic_item`` argument is a ``(type, item)`` pair; the returned
    ``statistic_item`` field holds that statistic (``:MEASure:STATistic:ITEM?``).
    Both measure against ``:MEASure:SOURce``, except the two-source items
    (``RPHase``/``FPHase``, ``RDELay``/``FDELay``) which take their operands from
    ``setup_psa``/``psb`` and ``setup_dsa``/``dsb``.

    Args:
        item (str): Item to measure instantaneously (e.g. ``VPP``, ``FREQuency``).
        statistic_item (tuple): A ``(type, item)`` pair mirroring
            ``:STATistic:ITEM? <type>,<item>``, where ``type`` is ``MAX``/``MIN``/
            ``CURR``/``AVER``/``DEV``; only types valid in the active
            ``statistic_mode`` return a number (others are ``nan``).
        source (int, str): ``:MEASure:SOURce`` (a channel number or ``MATH``).
        counter_source (int, str): ``:MEASure:COUNter:SOURce`` (a channel or
            ``OFF``). After enabling a channel the counter needs time to gate, so
            ``counter_value`` in the same call may be stale; let it settle (e.g.
            ``sleep``) before reading it. It reads 0 while the source is ``OFF``.
        setup_max (int): ``:MEASure:SETup:MAX`` upper threshold %, 7 to 95.
        setup_mid (int): ``:MEASure:SETup:MID`` middle threshold %, 6 to 94.
        setup_min (int): ``:MEASure:SETup:MIN`` lower threshold %, 5 to 93.
        setup_psa (int, str): ``:MEASure:SETup:PSA`` phase source A.
        setup_psb (int, str): ``:MEASure:SETup:PSB`` phase source B.
        setup_dsa (int, str): ``:MEASure:SETup:DSA`` delay source A.
        setup_dsb (int, str): ``:MEASure:SETup:DSB`` delay source B.
        statistic_mode (str): ``:MEASure:STATistic:MODE`` (``EXTRemum`` reports
            min/max, ``DIFFerence`` reports deviation/count).
        statistic_display (bool): ``:MEASure:STATistic:DISPlay``.
        statistic_reset (bool): When ``True``, send ``:MEASure:STATistic:RESet``.
        clear (str): ``:MEASure:CLEar`` (``ITEM1`` through ``ITEM5`` or ``ALL``).

    Returns:
        A namedtuple with a field for each argument, queried back regardless of
        which were provided, plus the read-only ``counter_value``
        (``:MEASure:COUNter:VALue?``). ``item`` and ``statistic_item`` read back the
        measured value, or ``None`` when that item was not requested.
    """
    provided = dict(
        source=source,
        counter_source=counter_source,
        setup_max=setup_max,
        setup_mid=setup_mid,
        setup_min=setup_min,
        setup_psa=setup_psa,
        setup_psb=setup_psb,
        setup_dsa=setup_dsa,
        setup_dsb=setup_dsb,
        statistic_mode=statistic_mode,
        statistic_display=statistic_display,
        item=item,
        statistic_item=statistic_item,
    )
    if statistic_reset:
        oscope.write(":MEAS:STAT:RES")  # write-only action; no :STAT:RESet? query
    if clear is not None:
        oscope.write(":MEAS:CLE " + clear)  # write-only action; no :CLEar? query
    write_fields(oscope, _SETTABLE, provided)

    return MEASURE(
        **read_fields(
            oscope,
            _SETTABLE + _READONLY,
            item=item,
            statistic_item=statistic_item,
        )
    )
