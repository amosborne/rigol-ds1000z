from functools import partial
from time import sleep
from typing import Optional

from pyvisa import ResourceManager

from .channel import channel
from .display import display
from .ieee import ieee
from .timebase import timebase
from .waveform import waveform


class Rigol_DS1000Z:
    def __init__(self, visa: str):
        self.visa_name = visa
        self.ieee = partial(ieee, self)
        self.channel = partial(channel, self)
        self.timebase = partial(timebase, self)
        self.display = partial(display, self)
        self.waveform = partial(waveform, self)

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

    def run(self):
        self.write(":RUN")

    def stop(self):
        self.write(":STOP")

    def single(self):
        self.write(":SING")

    def tforce(self):
        self.write(":TFOR")
