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
from rigol_ds1000z.utils import find_visa


class Rigol_DS1000Z:
    def __init__(self, visa: Optional[str] = None):
        self.visa_name = find_visa() if visa is None else visa
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
        self.visa_rsrc = ResourceManager().open_resource(self.visa_name)
        return self

    def close(self):
        self.visa_rsrc.close()

    def write(self, cmd: str):
        self.visa_rsrc.write(cmd + ";*WAI")

    def read(self):
        return self.visa_rsrc.read().strip()

    def query(self, cmd: str, delay: Optional[float] = None):
        return self.visa_rsrc.query(cmd + ";*WAI", delay).strip()

    def autoscale(self):
        self.write(":AUT")
        sleep(10)

    def clear(self):
        self.write(":CLE")
        sleep(1)

    def run(self):
        self.write(":RUN")
        sleep(1)

    def stop(self):
        self.write(":STOP")
        sleep(1)

    def single(self):
        self.write(":SING")
        sleep(1)

    def tforce(self):
        self.write(":TFOR")
        sleep(1)
