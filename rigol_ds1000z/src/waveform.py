from collections import namedtuple
from typing import Optional, Union

from rigol_ds1000z.src._scpi import (
    Binary,
    Int,
    Source,
    String,
    read_fields,
    write_fields,
)

WAVEFORM = namedtuple(
    "WAVEFORM",
    (
        "source mode format data xincrement xorigin xreference "
        "yincrement yorigin yreference start stop points count"
    ),
)

# settable parameters (written when provided, then read back)
_SETTABLE = (
    Source("source", ":WAV:SOUR"),
    String("mode", ":WAV:MODE"),
    String("format", ":WAV:FORM"),
    Int("start", ":WAV:STAR"),
    Int("stop", ":WAV:STOP"),
)


def _read_data(oscope, format):
    """Read ``:WAV:DATA?`` using the transfer method for the given format."""
    if format == "ASC":
        return String("data", ":WAV:DATA").get(oscope)
    if format == "BYTE":
        return Binary("data", ":WAV:DATA", "B").get(oscope)
    if format == "WORD":
        return Binary("data", ":WAV:DATA", "H").get(oscope)
    return None


def _read_preamble(oscope):
    """Parse ``:WAV:PRE?`` for the sample/average counts and the X/Y scaling."""
    p = String("preamble", ":WAV:PRE").get(oscope).split(",")
    return {
        "points": int(p[2]),
        "count": int(p[3]),
        "xincrement": float(p[4]),
        "xorigin": float(p[5]),
        "xreference": int(p[6]),
        "yincrement": float(p[7]),
        "yorigin": int(p[8]),
        "yreference": int(p[9]),
    }


def waveform(
    oscope,
    source: Union[int, str, None] = None,
    mode: Optional[str] = None,
    format: Optional[str] = None,
    start: Optional[int] = None,
    stop: Optional[int] = None,
):
    """
    Send commands to control an oscilloscope's waveform data capturing.
    All arguments are optional.

    Args:
        source (int, str): ``:WAVeform:SOURce``
        mode (str): ``:WAVeform:MODE``
        format (str): ``:WAVeform:FORMat``
        start (int): ``:WAVeform:STARt``
        stop (int): ``:WAVeform:STOP``

    Returns:
        A namedtuple with fields corresponding to the named arguments of this function.
        All fields are queried regardless of which arguments were initially provided.
        The ``data`` field holds the captured samples (``:WAVeform:DATA?``). The
        ``points`` and ``count`` fields and the X/Y scaling factors used for
        post-processing are parsed from ``:WAVeform:PREamble?``.
    """
    provided = dict(source=source, mode=mode, format=format, start=start, stop=stop)
    write_fields(oscope, _SETTABLE, provided)
    values = read_fields(oscope, _SETTABLE)
    return WAVEFORM(
        **values,
        data=_read_data(oscope, values["format"]),
        **_read_preamble(oscope),
    )
