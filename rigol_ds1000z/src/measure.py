from collections import namedtuple
from math import nan
from time import sleep
from typing import Optional, Union

MEASURE = namedtuple("MEASURE", "source counter item value statistics")
STATISTICS = namedtuple("STATISTICS", "maximum minimum current average deviation")


def _to_float(response):
    """Parse a measurement query response to float.

    The scope returns non-numeric text for a measurement it cannot compute
    (e.g. ``"measure error!"`` for a rise time with no clean edge on screen).
    Treat any non-numeric response as ``nan`` ("unavailable") instead of
    crashing — it sits alongside the ``9.9e37`` invalid-measurement sentinel the
    scope uses elsewhere.
    """
    try:
        return float(response)
    except (TypeError, ValueError):
        return nan

# Measurement item mnemonics accepted by ``item`` (DS1000Z programming guide).
ITEMS = (
    "VMAX", "VMIN", "VPP", "VTOP", "VBASe", "VAMP", "VAVG", "VRMS",
    "OVERshoot", "PREShoot", "MARea", "MPARea", "PERiod", "FREQuency",
    "RTIMe", "FTIMe", "PWIDth", "NWIDth", "PDUTy", "NDUTy", "TVMAX", "TVMIN",
    "PSLEWrate", "NSLEWrate", "VUPper", "VMID", "VLOWer", "VARIance",
    "PVRMs", "PPULses", "NPULses", "PEDGes", "NEDGes",
)  # fmt: skip


def _source_token(source):
    """Format a channel source as either ``CHAN<n>`` (int) or a literal (str)."""
    return source if isinstance(source, str) else "CHAN{:d}".format(source)


def measure(
    oscope,
    source: Union[int, str, None] = None,
    counter: Union[int, str, None] = None,
    item: Optional[str] = None,
    clear: Optional[str] = None,
    statistics: Optional[bool] = None,
):
    """
    Send commands to make automatic measurements on an oscilloscope.
    All arguments are optional. The ``source`` is the default channel used for
    item measurements; an ``item`` query returns its measured ``value`` against
    that source. See ``measure.ITEMS`` for the supported item mnemonics
    (e.g. ``VPP``, ``VAVG``, ``FREQuency``, ``PERiod``, ``PWIDth``).

    Args:
        source (int, str): ``:MEASure:SOURce`` (a channel number or ``MATH``).
        counter (int, str): ``:MEASure:COUNter:SOURce`` (a channel or ``OFF``);
            setting it is followed by a 1s delay so the counter can gate.
        item (str): The measurement item to query via ``:MEASure:ITEM?``.
        clear (str): ``:MEASure:CLEar`` (``ITEM1`` through ``ITEM5`` or ``ALL``).
        statistics (bool): When ``True`` and an ``item`` is given, enable the
            statistics display (``:MEASure:STATistic:DISPlay``) and report the
            item's statistics.

    Returns:
        A namedtuple with fields ``source``, ``counter``, ``item``, ``value``,
        and ``statistics``. ``source`` and ``counter`` are always queried.
        ``counter`` is the frequency counter value (``:MEASure:COUNter:VALue?``)
        or ``None`` when the counter source is ``OFF``. ``item`` echoes the
        queried item and ``value`` is its float result, both ``None`` when no
        ``item`` was given. ``statistics`` is a ``STATISTICS`` namedtuple
        (``maximum``, ``minimum``, ``current``, ``average``, ``deviation``)
        when requested, otherwise ``None``.
    """
    if source is not None:
        oscope.write(":MEAS:SOUR " + _source_token(source))

    if counter is not None:
        oscope.write(":MEAS:COUN:SOUR " + _source_token(counter))
        sleep(1)  # allow the frequency counter to gate before its value is read

    if clear is not None:
        oscope.write(":MEAS:CLE " + clear)

    source_query = oscope.query(":MEAS:SOUR?")
    if source_query.startswith("CHAN"):
        source_query = int(source_query[-1])

    counter_source = oscope.query(":MEAS:COUN:SOUR?")
    counter_value = (
        None if counter_source == "OFF" else _to_float(oscope.query(":MEAS:COUN:VAL?"))
    )

    value = None
    statistics_query = None
    if item is not None:
        src = _source_token(source_query)
        value = _to_float(oscope.query(":MEAS:ITEM? {:s},{:s}".format(item, src)))

        if statistics:
            oscope.write(":MEAS:STAT:DISP 1")
            oscope.write(":MEAS:STAT:ITEM {:s},{:s}".format(item, src))

            def _stat(kind):
                query = ":MEAS:STAT:ITEM? {:s},{:s}".format(kind, item)
                return _to_float(oscope.query(query))

            statistics_query = STATISTICS(
                maximum=_stat("MAX"),
                minimum=_stat("MIN"),
                current=_stat("CURR"),
                average=_stat("AVER"),
                deviation=_stat("DEV"),
            )

    return MEASURE(
        source=source_query,
        counter=counter_value,
        item=item,
        value=value,
        statistics=statistics_query,
    )
