from collections import namedtuple
from typing import Optional, Union

WAVEFORM = namedtuple(
    "WAVEFORM",
    (
        "source mode format data xincrement xorigin xreference "
        "yincrement yorigin yreference start stop preamble"
    ),
)


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
        The ``data`` field is additionally provided as a result of the query ``:WAVeform:DATA?``.
        There are several other fields provided as well which are required for post-processing.
    """
    if source is not None:
        if isinstance(source, str):
            oscope.write(":WAV:SOUR " + source)
        else:
            oscope.write(":WAV:SOUR CHAN{:d}".format(source))

    source_query = oscope.query(":WAV:SOUR?")
    if not source_query == "MATH":
        source_query = int(source_query[-1])

    if mode is not None:
        oscope.write(":WAV:MODE " + mode)

    if format is not None:
        oscope.write(":WAV:FORM " + format)

    format_query = oscope.query(":WAV:FORM?")

    if start is not None:
        oscope.write(":WAV:STAR {:d}".format(start))

    if stop is not None:
        oscope.write(":WAV:STOP {:d}".format(stop))

    if format_query == "ASC":
        data_query = oscope.query(":WAV:DATA?")
    elif format_query == "BYTE":
        data_query = oscope.visa_rsrc.query_binary_values(":WAV:DATA?", "B")
    elif format_query == "WORD":
        data_query = oscope.visa_rsrc.query_binary_values(":WAV:DATA?", "H")
    else:
        data_query = None

    return WAVEFORM(
        source=source_query,
        mode=oscope.query(":WAV:MODE?"),
        format=format_query,
        data=data_query,
        xincrement=float(oscope.query(":WAV:XINC?")),
        xorigin=float(oscope.query(":WAV:XOR?")),
        xreference=int(oscope.query(":WAV:XREF?")),
        yincrement=float(oscope.query(":WAV:YINC?")),
        yorigin=int(oscope.query(":WAV:YOR?")),
        yreference=int(oscope.query(":WAV:YREF?")),
        start=int(oscope.query(":WAV:STAR?")),
        stop=int(oscope.query(":WAV:STOP?")),
        preamble=oscope.query(":WAV:PRE?"),
    )
