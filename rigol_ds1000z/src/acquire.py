from collections import namedtuple
from typing import Optional, Union

from rigol_ds1000z.src._scpi import Float, Int, String, read_fields, write_fields

ACQUIRE = namedtuple("ACQUIRE", "averages mdepth srate type")

# ``type`` is declared first so it is written before ``averages`` (averages only
# takes effect while the type is AVERages). ``mdepth`` is an integer point count
# or the literal ``AUTO`` (an Int with ``AUTO`` as a pass-through keyword).
_SETTABLE = (
    String("type", ":ACQ:TYPE"),
    Int("averages", ":ACQ:AVER"),
    Int("mdepth", ":ACQ:MDEP", keywords=("AUTO",)),
)

# read-only fields (queried, never written)
_READONLY = (Float("srate", ":ACQ:SRAT"),)


def acquire(
    oscope,
    averages: Optional[int] = None,
    mdepth: Union[int, str, None] = None,
    type: Optional[str] = None,
):
    """
    Send commands to control an oscilloscope's acquisition behavior.
    All arguments are optional. ``averages`` only takes effect while the
    acquisition ``type`` is ``AVERages``; when both are specified the
    ``type`` command is issued first.

    Args:
        averages (int): ``:ACQuire:AVERages`` (a power of two, 2 to 1024).
        mdepth (int, str): ``:ACQuire:MDEPth`` (an integer point count or ``AUTO``).
        type (str): ``:ACQuire:TYPE`` (``NORM``, ``AVER``, ``PEAK``, or ``HRES``).

    Returns:
        A namedtuple with fields corresponding to the named arguments of this function.
        All fields are queried regardless of which arguments were initially provided.
        The ``srate`` field is additionally provided as a result of the
        query ``:ACQuire:SRATe?`` (the sample rate in samples per second).
    """
    provided = dict(type=type, averages=averages, mdepth=mdepth)
    write_fields(oscope, _SETTABLE, provided)
    return ACQUIRE(**read_fields(oscope, _SETTABLE + _READONLY))
