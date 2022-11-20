from functools import partial
from time import sleep
from typing import Optional

from pyvisa import ResourceManager

from rigol_ds1000z.src.channel import channel
from rigol_ds1000z.src.display import display
from rigol_ds1000z.src.ieee import ieee
from rigol_ds1000z.src.timebase import timebase
from rigol_ds1000z.src.trigger import trigger
from rigol_ds1000z.src.waveform import waveform
from rigol_ds1000z.utils import find_visas


class Rigol_DS1000Z:
    """
    A class for communicating with a Rigol DS1000Z series oscilloscope.
    This class is compatible with context managers. The functional interfaces
    ``ieee``, ``channel``, ``timebase``, ``display``, ``waveform``, and ``trigger``
    are bound to this object as partial functions.

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

        self.ieee = partial(ieee, self)
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
        self.visa_rsrc = ResourceManager(self.visa_backend).open_resource(
            self.visa_name
        )
        return self

    def close(self):
        """Close the VISA resource to terminate the communication channel."""
        self.visa_rsrc.close()

    def write(self, cmd: str):
        """
        Write a command over the VISA communication interface.
        The command is automatically appended with a ``*WAI`` command.

        Args:
            cmd (str): The command string to be written.
        """
        self.visa_rsrc.write(cmd + ";*WAI")

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
        The command is automatically appended with a ``*WAI`` command.

        Args:
            cmd (str): The command string to be written.
            delay (float): Time delay between write and read (optional).

        Returns:
            The received string.
        """
        return self.visa_rsrc.query(cmd + ";*WAI", delay).strip()

    def autoscale(self):
        """``:AUToscale`` Autoscale the oscilloscope, followed by a 10s delay."""
        self.write(":AUT")
        sleep(10)

    def clear(self):
        """``:CLEar`` Clear the oscilloscope display, followed by a 1s delay."""
        self.write(":CLE")
        sleep(1)

    def run(self):
        """``:RUN`` Run the oscilloscope, followed by a 1s delay."""
        self.write(":RUN")
        sleep(1)

    def stop(self):
        """``:STOP`` Stop the oscilloscope, followed by a 1s delay."""
        self.write(":STOP")
        sleep(1)

    def single(self):
        """``:SINGle`` Single trigger the oscilloscope, followed by a 1s delay."""
        self.write(":SING")
        sleep(1)

    def tforce(self):
        """``:TFORce`` Force trigger the oscilloscope, followed by a 1s delay."""
        self.write(":TFOR")
        sleep(1)
