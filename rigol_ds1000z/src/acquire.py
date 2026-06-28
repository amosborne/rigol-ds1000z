from collections import namedtuple
from typing import Optional, Union

ACQUIRE = namedtuple("ACQUIRE", "averages memdepth srate type")


def acquire(
    oscope,
    averages: Optional[int] = None,
    memdepth: Union[int, str, None] = None,
    type: Optional[str] = None,
):
    """
    Send commands to control an oscilloscope's acquisition behavior.
    All arguments are optional. ``averages`` only takes effect while the
    acquisition ``type`` is ``AVERages``; when both are specified the
    ``type`` command is issued first.

    Args:
        averages (int): ``:ACQuire:AVERages`` (a power of two, 2 to 1024).
        memdepth (int, str): ``:ACQuire:MDEPth`` (an integer point count or ``AUTO``).
        type (str): ``:ACQuire:TYPE`` (``NORM``, ``AVER``, ``PEAK``, or ``HRES``).

    Returns:
        A namedtuple with fields corresponding to the named arguments of this function.
        All fields are queried regardless of which arguments were initially provided.
        The ``srate`` field is additionally provided as a result of the
        query ``:ACQuire:SRATe?`` (the sample rate in samples per second).
    """
    if type is not None:
        oscope.write(":ACQ:TYPE {:s}".format(type))

    if averages is not None:
        oscope.write(":ACQ:AVER {:d}".format(averages))

    if memdepth is not None:
        oscope.write(":ACQ:MDEP {}".format(memdepth))

    return ACQUIRE(
        averages=int(oscope.query(":ACQ:AVER?")),
        memdepth=oscope.query(":ACQ:MDEP?"),
        srate=float(oscope.query(":ACQ:SRAT?")),
        type=oscope.query(":ACQ:TYPE?"),
    )
