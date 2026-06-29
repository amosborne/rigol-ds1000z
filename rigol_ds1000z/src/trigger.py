from collections import namedtuple
from typing import TYPE_CHECKING, Optional, Union

from rigol_ds1000z.src._scpi import (
    Bool,
    Float,
    Int,
    Source,
    String,
    read_fields,
    write_fields,
)

if TYPE_CHECKING:
    from rigol_ds1000z.src.oscope import Rigol_DS1000Z

TRIGGER = namedtuple(
    "TRIGGER",
    "sweep holdoff nreject mode "
    "coupling edge_source edge_slope edge_level "
    "pulse_source pulse_when pulse_width pulse_uwidth pulse_lwidth pulse_level "
    "slope_source slope_when slope_time slope_tupper slope_tlower slope_window "
    "slope_alevel slope_blevel status position",
)

# top-level controls -- written when provided and always queried back
_TOP = (
    String("sweep", ":TRIG:SWE"),
    Float("holdoff", ":TRIG:HOLD"),
    Bool("nreject", ":TRIG:NREJ"),
    String("mode", ":TRIG:MODE"),
)

# top-level, query-only
_READONLY = (
    String("status", ":TRIG:STAT"),
    Int("position", ":TRIG:POS"),
)

# per-mode parameters -- read back only while that mode is active, so an inactive
# mode's query never errors (``coupling`` is an edge-only top-level command)
_EDGE = (
    String("coupling", ":TRIG:COUP"),
    Source("edge_source", ":TRIG:EDG:SOUR"),
    String("edge_slope", ":TRIG:EDG:SLOP"),
    Float("edge_level", ":TRIG:EDG:LEV"),
)
_PULSE = (
    Source("pulse_source", ":TRIG:PULS:SOUR"),
    String("pulse_when", ":TRIG:PULS:WHEN"),
    Float("pulse_width", ":TRIG:PULS:WIDT"),
    Float("pulse_uwidth", ":TRIG:PULS:UWID"),
    Float("pulse_lwidth", ":TRIG:PULS:LWID"),
    Float("pulse_level", ":TRIG:PULS:LEV"),
)
_SLOPE = (
    Source("slope_source", ":TRIG:SLOP:SOUR"),
    String("slope_when", ":TRIG:SLOP:WHEN"),
    Float("slope_time", ":TRIG:SLOP:TIME"),
    Float("slope_tupper", ":TRIG:SLOP:TUPP"),
    Float("slope_tlower", ":TRIG:SLOP:TLOW"),
    String("slope_window", ":TRIG:SLOP:WIND"),
    Float("slope_alevel", ":TRIG:SLOP:ALEV"),
    Float("slope_blevel", ":TRIG:SLOP:BLEV"),
)

_MODES = {"EDGE": _EDGE, "PULS": _PULSE, "SLOP": _SLOPE}
_SETTABLE = _TOP + _EDGE + _PULSE + _SLOPE


def trigger(
    oscope: "Rigol_DS1000Z",
    sweep: Optional[str] = None,
    holdoff: Optional[float] = None,
    nreject: Optional[bool] = None,
    mode: Optional[str] = None,
    coupling: Optional[str] = None,
    edge_source: Union[int, str, None] = None,
    edge_slope: Optional[str] = None,
    edge_level: Optional[float] = None,
    pulse_source: Union[int, str, None] = None,
    pulse_when: Optional[str] = None,
    pulse_width: Optional[float] = None,
    pulse_uwidth: Optional[float] = None,
    pulse_lwidth: Optional[float] = None,
    pulse_level: Optional[float] = None,
    slope_source: Union[int, str, None] = None,
    slope_when: Optional[str] = None,
    slope_time: Optional[float] = None,
    slope_tupper: Optional[float] = None,
    slope_tlower: Optional[float] = None,
    slope_window: Optional[str] = None,
    slope_alevel: Optional[float] = None,
    slope_blevel: Optional[float] = None,
):
    """
    Send commands to control an oscilloscope's trigger system.
    All arguments are optional. Field names mirror the SCPI command tree
    (``edge_level`` <- ``:TRIGger:EDGe:LEVel``). Provided fields are written, then
    the top-level fields and the fields of the *active* ``:TRIGger:MODE`` are
    queried back; the other modes' fields come back ``None``.

    Args:
        sweep (str): ``:TRIGger:SWEep`` (``AUTO``/``NORMal``/``SINGle``). Setting
            ``SINGle`` arms one acquisition; let it settle (e.g. ``sleep``) before
            reading ``status``.
        holdoff (float): ``:TRIGger:HOLDoff`` (16ns to 10s).
        nreject (bool): ``:TRIGger:NREJect`` noise rejection.
        mode (str): ``:TRIGger:MODE`` (``EDGE``/``PULSe``/``SLOPe``).
        coupling (str): ``:TRIGger:COUPling`` (``AC``/``DC``/``LFReject``/
            ``HFReject``); edge trigger only.
        edge_source (int, str): ``:TRIGger:EDGe:SOURce`` (a channel or ``AC``).
        edge_slope (str): ``:TRIGger:EDGe:SLOPe`` (``POSitive``/``NEGative``/``RFALl``).
        edge_level (float): ``:TRIGger:EDGe:LEVel``.
        pulse_source (int, str): ``:TRIGger:PULSe:SOURce``.
        pulse_when (str): ``:TRIGger:PULSe:WHEN`` (``PGReater``/``PLESs``/
            ``NGReater``/``NLESs``/``PGLess``/``NGLess``).
        pulse_width (float): ``:TRIGger:PULSe:WIDTh`` (single-threshold ``WHEN``).
        pulse_uwidth (float): ``:TRIGger:PULSe:UWIDth`` (``PGLess``/``NGLess``).
        pulse_lwidth (float): ``:TRIGger:PULSe:LWIDth`` (``PGLess``/``NGLess``).
        pulse_level (float): ``:TRIGger:PULSe:LEVel``.
        slope_source (int, str): ``:TRIGger:SLOPe:SOURce``.
        slope_when (str): ``:TRIGger:SLOPe:WHEN`` (same set as ``pulse_when``).
        slope_time (float): ``:TRIGger:SLOPe:TIME`` (single-threshold ``WHEN``).
        slope_tupper (float): ``:TRIGger:SLOPe:TUPPer`` (``PGLess``/``NGLess``).
        slope_tlower (float): ``:TRIGger:SLOPe:TLOWer`` (``PGLess``/``NGLess``).
        slope_window (str): ``:TRIGger:SLOPe:WINDow`` (``TA``/``TB``/``TAB``).
        slope_alevel (float): ``:TRIGger:SLOPe:ALEVel`` (upper trigger level).
        slope_blevel (float): ``:TRIGger:SLOPe:BLEVel`` (lower trigger level).

    Returns:
        A namedtuple with a field for each argument, queried back regardless of
        which were provided, plus the read-only ``status`` (``:TRIGger:STATus?``)
        and ``position`` (``:TRIGger:POSition?``). Fields belonging to a non-active
        mode are ``None``.
    """
    provided = dict(
        sweep=sweep,
        holdoff=holdoff,
        nreject=nreject,
        mode=mode,
        coupling=coupling,
        edge_source=edge_source,
        edge_slope=edge_slope,
        edge_level=edge_level,
        pulse_source=pulse_source,
        pulse_when=pulse_when,
        pulse_width=pulse_width,
        pulse_uwidth=pulse_uwidth,
        pulse_lwidth=pulse_lwidth,
        pulse_level=pulse_level,
        slope_source=slope_source,
        slope_when=slope_when,
        slope_time=slope_time,
        slope_tupper=slope_tupper,
        slope_tlower=slope_tlower,
        slope_window=slope_window,
        slope_alevel=slope_alevel,
        slope_blevel=slope_blevel,
    )
    write_fields(oscope, _SETTABLE, provided)

    values = read_fields(oscope, _TOP + _READONLY)
    values.update(read_fields(oscope, _MODES.get(values["mode"], ())))
    return TRIGGER(**{name: values.get(name) for name in TRIGGER._fields})
