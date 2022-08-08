from collections import namedtuple
from time import sleep
from typing import Optional, Union

TRIGGER = namedtuple(
    "TRIGGER",
    "status sweep noisereject mode holdoff coupling source slope level",
    defaults=(None,) * 5,  # (status, sweep, noisereject, mode) are required
)


def trigger(
    oscope,
    sweep: Optional[str] = None,
    noisereject: Optional[bool] = None,
    mode: Optional[str] = None,
    holdoff: Optional[float] = None,
    coupling: Optional[str] = None,
    source: Union[int, str, None] = None,
    slope: Optional[str] = None,
    level: Optional[float] = None,
):
    """
    Send commands to control an oscilloscope's triggering behavior.
    This interface is only partially implemented so as to support edge-triggering.
    All arguments are optional. Depending on the triggering mode, only
    the applicable arguments are utilized by the relevant helper function.

    Args:
        sweep (str): ``:TRIGger:SWEep``
        noisereject (bool): ``:TRIGger:NREJect``
        mode (str): ``:TRIGger:MODE``
        holdoff (float): See helper functions.
        coupling (str): See helper functions.
        source (int, str): See helper functions.
        slope (str): See helper functions.
        level (float): See helper functions.

    Returns:
        A namedtuple with fields corresponding to the named arguments of this function.
        All fields are queried regardless of which arguments were initially provided.
        The ``status`` field is additionally provided as a result of the query ``:TRIGger:STATus?``.
    """
    if sweep is not None:
        oscope.write(":TRIG:SWE {:s}".format(sweep))
        sleep(1)

    if noisereject is not None:
        oscope.write(":TRIG:NREJ {:d}".format(noisereject))

    if mode is not None:
        oscope.write(":TRIG:MODE {:s}".format(mode))

    trigger_query = TRIGGER(
        status=oscope.query(":TRIG:STAT?"),
        sweep=oscope.query(":TRIG:SWE?"),
        noisereject=bool(int(oscope.query(":TRIG:NREJ?"))),
        mode=oscope.query(":TRIG:MODE?"),
    )

    if trigger_query.mode == "EDGE":
        return trigger_edge(
            oscope, trigger_query, holdoff, coupling, source, slope, level
        )

    return trigger_query


def trigger_edge(oscope, trigger_query, holdoff, coupling, source, slope, level):
    """
    Helper function to configure edge-triggering, ``:TRIGger:MODE EDGE``.

    Args:
        holdoff (float): ``:TRIGger:HOLDoff``
        coupling (str): ``:TRIGger:COUPling``
        source (int, str): ``:TRIGger:EDGe:SOURce``
        slope (str): ``:TRIGger:EDGe:SLOPe``
        level (float): ``:TRIGger:EDGe:LEVel``
    """
    if holdoff is not None:
        oscope.write(":TRIG:HOLD {:0.10f}".format(holdoff))

    if coupling is not None:
        oscope.write(":TRIG:COUP {:s}".format(coupling))

    if source is not None:
        if isinstance(source, str):
            oscope.write(":TRIG:EDG:SOUR {:s}".format(source))
        else:
            oscope.write(":TRIG:EDG:SOUR CHAN{:d}".format(source))

    if slope is not None:
        oscope.write(":TRIG:EDG:SLOP {:s}".format(slope))

    if level is not None:
        oscope.write("TRIG:EDG:LEV {:0.10f}".format(level))

    source_query = oscope.query(":TRIG:EDG:SOUR?")
    if not source_query == "AC":
        source_query = int(source_query[-1])

    return trigger_query._replace(
        holdoff=float(oscope.query(":TRIG:HOLD?")),
        coupling=oscope.query(":TRIG:COUP?"),
        source=source_query,
        slope=oscope.query(":TRIG:EDG:SLOP?"),
        level=float(oscope.query(":TRIG:EDG:LEV?")),
    )
