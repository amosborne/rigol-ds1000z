from collections import namedtuple
from time import sleep
from typing import Optional, Union

TRIGGER = namedtuple(
    "TRIGGER",
    "status sweep noisereject mode holdoff coupling source slope level "
    "when upper lower window alevel blevel time",
    defaults=(None,) * 12,  # (status, sweep, noisereject, mode) are required
)


def _source_token(source):
    """Format a channel source as either ``CHAN<n>`` (int) or a literal (str)."""
    return source if isinstance(source, str) else "CHAN{:d}".format(source)


def _source_value(query):
    """Coerce a queried source into an int channel number or a literal string.

    Any non-channel source (such as ``AC`` or ``EXT``) is returned verbatim
    rather than being passed to ``int()``, which the original code would only
    avoid for the literal ``AC``.
    """
    return int(query[-1]) if query.startswith("CHAN") else query


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
    when: Optional[str] = None,
    upper: Optional[float] = None,
    lower: Optional[float] = None,
    window: Optional[str] = None,
    alevel: Optional[float] = None,
    blevel: Optional[float] = None,
    time: Optional[float] = None,
):
    """
    Send commands to control an oscilloscope's triggering behavior.
    The ``EDGE``, ``PULSe``, and ``SLOPe`` trigger modes are supported.
    All arguments are optional. Depending on the triggering mode, only the
    applicable arguments are utilized by the relevant helper function.

    Args:
        sweep (str): ``:TRIGger:SWEep``
        noisereject (bool): ``:TRIGger:NREJect``
        mode (str): ``:TRIGger:MODE``
        holdoff (float): See ``trigger_edge``.
        coupling (str): See ``trigger_edge``.
        source (int, str): See helper functions.
        slope (str): See ``trigger_edge``.
        level (float): See ``trigger_edge``, ``trigger_pulse``.
        when (str): See ``trigger_pulse``, ``trigger_slope``.
        upper (float): See ``trigger_pulse``, ``trigger_slope``.
        lower (float): See ``trigger_pulse``, ``trigger_slope``.
        window (str): See ``trigger_slope``.
        alevel (float): See ``trigger_slope``.
        blevel (float): See ``trigger_slope``.
        time (float): See ``trigger_slope``.

    Returns:
        A namedtuple with fields corresponding to the named arguments of this function.
        All fields applicable to the active mode are queried regardless of which
        arguments were initially provided; fields for other modes are ``None``.
        The ``status`` field is additionally provided as a result of the query
        ``:TRIGger:STATus?``.
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

    if trigger_query.mode == "PULS":
        return trigger_pulse(oscope, trigger_query, source, when, level, upper, lower)

    if trigger_query.mode == "SLOP":
        return trigger_slope(
            oscope,
            trigger_query,
            source,
            when,
            time,
            upper,
            lower,
            window,
            alevel,
            blevel,
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
        oscope.write(":TRIG:EDG:SOUR " + _source_token(source))

    if slope is not None:
        oscope.write(":TRIG:EDG:SLOP {:s}".format(slope))

    if level is not None:
        oscope.write(":TRIG:EDG:LEV {:0.10f}".format(level))

    return trigger_query._replace(
        holdoff=float(oscope.query(":TRIG:HOLD?")),
        coupling=oscope.query(":TRIG:COUP?"),
        source=_source_value(oscope.query(":TRIG:EDG:SOUR?")),
        slope=oscope.query(":TRIG:EDG:SLOP?"),
        level=float(oscope.query(":TRIG:EDG:LEV?")),
    )


def trigger_pulse(oscope, trigger_query, source, when, level, upper, lower):
    """
    Helper function to configure pulse-width triggering, ``:TRIGger:MODE PULSe``.

    Args:
        source (int, str): ``:TRIGger:PULSe:SOURce``
        when (str): ``:TRIGger:PULSe:WHEN`` (e.g. ``PGReater``, ``PLESs``, ``PGLess``).
        level (float): ``:TRIGger:PULSe:LEVel``
        upper (float): ``:TRIGger:PULSe:UWIDth``
        lower (float): ``:TRIGger:PULSe:LWIDth``
    """
    if source is not None:
        oscope.write(":TRIG:PULS:SOUR " + _source_token(source))

    if when is not None:
        oscope.write(":TRIG:PULS:WHEN {:s}".format(when))

    if level is not None:
        oscope.write(":TRIG:PULS:LEV {:0.10f}".format(level))

    if upper is not None:
        oscope.write(":TRIG:PULS:UWID {:0.10f}".format(upper))

    if lower is not None:
        oscope.write(":TRIG:PULS:LWID {:0.10f}".format(lower))

    return trigger_query._replace(
        source=_source_value(oscope.query(":TRIG:PULS:SOUR?")),
        when=oscope.query(":TRIG:PULS:WHEN?"),
        level=float(oscope.query(":TRIG:PULS:LEV?")),
        upper=float(oscope.query(":TRIG:PULS:UWID?")),
        lower=float(oscope.query(":TRIG:PULS:LWID?")),
    )


def trigger_slope(
    oscope,
    trigger_query,
    source,
    when,
    time,
    upper,
    lower,
    window,
    alevel,
    blevel,
):
    """
    Helper function to configure slope (rise/fall time) triggering,
    ``:TRIGger:MODE SLOPe``.

    Args:
        source (int, str): ``:TRIGger:SLOPe:SOURce``
        when (str): ``:TRIGger:SLOPe:WHEN`` (e.g. ``PGReater``, ``PLESs``, ``PGLess``).
        time (float): ``:TRIGger:SLOPe:TIME``
        upper (float): ``:TRIGger:SLOPe:TUPPer``
        lower (float): ``:TRIGger:SLOPe:TLOWer``
        window (str): ``:TRIGger:SLOPe:WINDow`` (``TA``, ``TB``, or ``TAB``).
        alevel (float): ``:TRIGger:SLOPe:ALEVel``
        blevel (float): ``:TRIGger:SLOPe:BLEVel``
    """
    if source is not None:
        oscope.write(":TRIG:SLOP:SOUR " + _source_token(source))

    if when is not None:
        oscope.write(":TRIG:SLOP:WHEN {:s}".format(when))

    if time is not None:
        oscope.write(":TRIG:SLOP:TIME {:0.10f}".format(time))

    if upper is not None:
        oscope.write(":TRIG:SLOP:TUPP {:0.10f}".format(upper))

    if lower is not None:
        oscope.write(":TRIG:SLOP:TLOW {:0.10f}".format(lower))

    if window is not None:
        oscope.write(":TRIG:SLOP:WIND {:s}".format(window))

    if alevel is not None:
        oscope.write(":TRIG:SLOP:ALEV {:0.10f}".format(alevel))

    if blevel is not None:
        oscope.write(":TRIG:SLOP:BLEV {:0.10f}".format(blevel))

    return trigger_query._replace(
        source=_source_value(oscope.query(":TRIG:SLOP:SOUR?")),
        when=oscope.query(":TRIG:SLOP:WHEN?"),
        time=float(oscope.query(":TRIG:SLOP:TIME?")),
        upper=float(oscope.query(":TRIG:SLOP:TUPP?")),
        lower=float(oscope.query(":TRIG:SLOP:TLOW?")),
        window=oscope.query(":TRIG:SLOP:WIND?"),
        alevel=float(oscope.query(":TRIG:SLOP:ALEV?")),
        blevel=float(oscope.query(":TRIG:SLOP:BLEV?")),
    )
