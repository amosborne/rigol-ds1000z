from functools import partial
from typing import Optional

from pyvisa import ResourceManager

from rigol_ds1000z.src.acquire import acquire
from rigol_ds1000z.src.channel import channel
from rigol_ds1000z.src.display import display
from rigol_ds1000z.src.measure import measure
from rigol_ds1000z.src.timebase import timebase
from rigol_ds1000z.src.trigger import trigger
from rigol_ds1000z.src.waveform import waveform
from rigol_ds1000z.utils import find_visas


class Rigol_DS1000Z:
    """
    A class for communicating with a Rigol DS1000Z series oscilloscope.
    This class is compatible with context managers. The functional interfaces
    ``acquire``, ``channel``, ``display``, ``measure``, ``timebase``,
    ``trigger``, and ``waveform`` are bound to this object as partial functions.
    IEEE 488.2 common commands (e.g. ``idn``, ``rst``, ``cls``, ``opc``) are
    available as methods.

    Args:
        visa (str): The VISA resource address string.
    """

    def __init__(self, visa: Optional[str] = None):
        visas = find_visas()

        if visa is None:
            self.visa_name, self.visa_backend = visas[0]
        else:
            self.visa_name = visa
            for visa, backend in visas:
                if self.visa_name == visa:
                    self.visa_backend = backend

        self.acquire = partial(acquire, self)
        self.channel = partial(channel, self)
        self.display = partial(display, self)
        self.measure = partial(measure, self)
        self.timebase = partial(timebase, self)
        self.trigger = partial(trigger, self)
        self.waveform = partial(waveform, self)

    def __enter__(self):
        return self.open()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        return self.close()

    def open(self):
        """Open the VISA resource to establish the communication channel."""
        self.visa_rsrc = ResourceManager(self.visa_backend).open_resource(
            self.visa_name
        )
        # Generous timeout so a blocking ``*OPC?`` outlasts the slowest operations
        # (``*RST`` ~6s, ``:AUToscale`` ~7s) rather than relying on fixed sleeps.
        self.visa_rsrc.timeout = 20000
        return self

    def close(self):
        """Close the VISA resource to terminate the communication channel."""
        self.visa_rsrc.close()

    def write(self, cmd: str):
        """
        Write a command over the VISA communication interface.

        Args:
            cmd (str): The command string to be written.
        """
        self.visa_rsrc.write(cmd)

    def read(self):
        """
        Read back over the VISA communication interface.

        Returns:
            The received string.
        """
        return self.visa_rsrc.read().strip()

    def query(self, cmd: str, delay: Optional[float] = None):
        """
        Execute a query over the VISA communication interface.
        The blocking read also synchronizes the controller to the response.

        Args:
            cmd (str): The command string to be written.
            delay (float): Time delay between write and read (optional).

        Returns:
            The received string.
        """
        return self.visa_rsrc.query(cmd, delay).strip()

    def cls(self):
        """``*CLS`` Clear the status registers."""
        self.write("*CLS")

    def ese(self, value: Optional[int] = None):
        """``*ESE`` Set (when given) and query the event status enable register."""
        if value is not None:
            self.write("*ESE {:d}".format(value))
        return int(self.query("*ESE?"))

    def esr(self):
        """``*ESR?`` Query (and clear) the event status register."""
        return int(self.query("*ESR?"))

    def idn(self):
        """``*IDN?`` Query the instrument identification string."""
        return self.query("*IDN?")

    def opc(self):
        """``*OPC?`` Block until all pending operations complete; returns ``True``."""
        return bool(int(self.query("*OPC?")))

    def rst(self):
        """``*RST`` Reset the instrument, blocking until the reset completes."""
        self.write("*RST")
        self.opc()

    def sre(self, value: Optional[int] = None):
        """``*SRE`` Set (when given) and query the service request enable register."""
        if value is not None:
            self.write("*SRE {:d}".format(value))
        return int(self.query("*SRE?"))

    def stb(self):
        """``*STB?`` Query the status byte register."""
        return int(self.query("*STB?"))

    def tst(self):
        """``*TST?`` Run the self-test; returns the result code (0 = pass)."""
        return int(self.query("*TST?"))

    def autoscale(self):
        """``:AUToscale`` Autoscale the oscilloscope, blocking until complete.

        Autoscale is an overlapped operation; completion is awaited via
        ``opc()`` (``*OPC?``), which blocks until the autoscale finishes.
        """
        self.write(":AUT")
        self.opc()

    def clear(self):
        """``:CLEar`` Clear the oscilloscope display."""
        self.write(":CLE")

    def run(self):
        """``:RUN`` Run the oscilloscope."""
        self.write(":RUN")

    def stop(self):
        """``:STOP`` Stop the oscilloscope."""
        self.write(":STOP")

    def single(self):
        """``:SINGle`` Arm a single-trigger acquisition."""
        self.write(":SING")

    def tforce(self):
        """``:TFORce`` Force a trigger."""
        self.write(":TFOR")
