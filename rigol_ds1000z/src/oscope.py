from functools import partial
from time import sleep
from typing import Optional

from pyvisa import ResourceManager

from rigol_ds1000z.src.channel import channel
from rigol_ds1000z.src.display import display
from rigol_ds1000z.src.timebase import timebase
from rigol_ds1000z.src.trigger import trigger
from rigol_ds1000z.src.waveform import waveform
from rigol_ds1000z.utils import find_visa, flush_buffer_hack


class Rigol_DS1000Z:
    """
    A class for communicating with a Rigol DS1000Z series oscilloscope.
    This class is compatible with context managers. The functional interfaces
    ``channel``, ``timebase``, ``display``, ``waveform``, and ``trigger``
    are bound to this object as partial functions.

    Args:
        visa (str): The VISA resource address string.
    """

    def __init__(self, visa: Optional[str] = None):
        self.visa_name, self.visa_backend = find_visa(visa)
        self.channel = partial(channel, self)
        self.timebase = partial(timebase, self)
        self.display = partial(display, self)
        self.waveform = partial(waveform, self)
        self.trigger = partial(trigger, self)

    def __enter__(self):
        return self.open()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        return self.close()

    def open(self):
        """Open the VISA resource to establish the communication channel."""
        self.visa_mngr = ResourceManager(self.visa_backend)
        self.visa_rsrc = self.visa_mngr.open_resource(self.visa_name)
        flush_buffer_hack(self.visa_rsrc)
        return self

    def close(self):
        """Close the VISA resource to terminate the communication channel."""
        self.visa_rsrc.close()
        self.visa_mngr.close()

    def write(self, cmd: str):
        """
        Write a command over the VISA communication interface.

        Args:
            cmd (str): The command string to be written.
        """
        self.visa_rsrc.write(cmd + ";*WAI")
        sleep(0.01)

    def read(self):
        """
        Read back over the VISA communication interface.

        Returns:
            The received string.
        """
        return self.visa_rsrc.read().strip()

    def query(self, cmd: str, delay: Optional[float] = 0.01):
        """
        Execute a query over the VISA communication interface.

        Args:
            cmd (str): The command string to be written.
            delay (float): Time delay between write and read (optional).

        Returns:
            The received string.
        """
        return self.visa_rsrc.query(cmd + ";*WAI", delay).strip()

    def autoscale(self, delay=15):
        """``:AUToscale`` Autoscale the oscilloscope."""
        self.write(":AUT")
        sleep(delay)

    def clear(self, delay=1):
        """``:CLEar`` Clear the oscilloscope display."""
        self.write(":CLE")
        sleep(delay)

    def run(self, delay=1):
        """``:RUN`` Run the oscilloscope."""
        self.write(":RUN")
        sleep(delay)

    def stop(self, delay=1):
        """``:STOP`` Stop the oscilloscope."""
        self.write(":STOP")
        sleep(delay)

    def single(self, delay=1):
        """``:SINGle`` Single trigger the oscilloscope."""
        self.write(":SING")
        sleep(delay)

    def tforce(self, delay=1):
        """``:TFORce`` Force trigger the oscilloscope."""
        self.write(":TFOR")
        sleep(delay)

    def rst(self, delay=15):
        """``*RST`` Restore the oscilloscope to the default state."""
        self.write("*RST")
        sleep(delay)
        flush_buffer_hack(self.visa_rsrc)

    def cls(self):
        """``*CLS`` Clear all the event registers and clear the error queue."""
        self.write("*CLS")

    def ese(self, value: Optional[int] = None):
        """``*ESE`` Set (int, optional) and query the enable standard event register."""
        if value is not None:
            self.write("*ESE {:d}".format(value))

        return int(self.query("*ESE?"))

    def esr(self):
        """``*ESR?`` Query and clear the event status register."""
        return int(self.query("*ESR?"))

    def idn(self):
        """``*IDN?`` Query the ID string of the oscilloscope."""
        return self.query("*IDN?")

    def sre(self, value: Optional[int] = None):
        """``*SRE`` Set (int, optional) and query the status byte register."""
        if value is not None:
            self.write("*SRE {:d}".format(value))

        return int(self.query("*SRE?"))

    def stb(self):
        """``*STB?`` Query and clear the status byte register."""
        return int(self.query("*STB?"))

    def tst(self):
        """``*TST?`` Perform a self-test."""
        return int(self.query("*TST?"))
