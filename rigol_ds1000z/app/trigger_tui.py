from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from textual.reactive import Reactive

from rigol_ds1000z import Rigol_DS1000Z
from rigol_ds1000z.app.channel_tui import Channel_TUI
from rigol_ds1000z.app.tablecontrol_tui import TableControl_TUI, _float2si

TRIGGER_MODES = {
    "EDGE": "Edge",
    "PULS": "Pulse",
    "RUNT": "Runt",
    "WIND": "Window",
    "NEDG": "Nth",
    "SLOP": "Slope",
    "VID": "Video",
    "PATT": "Pattern",
    "DEL": "Delay",
    "TIM": "Timeout",
    "DUR": "Duration",
    "SHOL": "StpHold",
    "RS232": "RS232",
    "IIC": "I2C",
    "SPI": "SPI",
}


class Trigger_TUI(TableControl_TUI):

    status: Reactive[RenderableType] = Reactive("")
    sweep: Reactive[RenderableType] = Reactive("")
    noisereject: Reactive[RenderableType] = Reactive("")
    mode: Reactive[RenderableType] = Reactive("")
    holdoff: Reactive[RenderableType] = Reactive("")
    coupling: Reactive[RenderableType] = Reactive("")
    source: Reactive[RenderableType] = Reactive("")
    slope: Reactive[RenderableType] = Reactive("")
    level: Reactive[RenderableType] = Reactive("")

    def __init__(self, oscope: Rigol_DS1000Z, channels) -> None:
        self.channels = channels
        super().__init__(oscope)

    def update_oscope(self, **kwargs):
        trigger = self.oscope.trigger(**kwargs)
        self.status = trigger.status
        self.sweep = trigger.sweep
        self.noisereject = "ON" if trigger.noisereject else "OFF"
        self.mode = TRIGGER_MODES[trigger.mode]
        self.holdoff = (
            _float2si(trigger.holdoff, sigfigs=3, unit="s")
            if trigger.mode == "EDGE"
            else None
        )
        self.coupling = trigger.coupling if trigger.mode == "EDGE" else None
        self.slope = trigger.slope if trigger.mode == "EDGE" else None
        self.level = (
            _float2si(
                trigger.level,
                sigfigs=3,
                unit=self.channels[trigger.source - 1].units[1],
            )
            if trigger.mode == "EDGE" and not trigger.source == "AC"
            else None
        )

        if trigger.mode == "EDGE":
            if isinstance(trigger.source, int):
                self.source = "CHAN{:d}".format(trigger.source)
            else:
                self.source = trigger.source
        else:
            self.source = None

    def render(self) -> RenderableType:
        table = Table(box=None, show_header=False)
        table.add_column(no_wrap=True)
        table.add_column(no_wrap=True)
        table.add_row("Status", self.status)
        table.add_row("Mode", self._create_field(field="sweep"))
        table.add_row("Type", self._create_field(field="mode"))

        if self.mode == "Edge":
            table.add_row("Source", self._create_field(field="source"))
            if self.source == "AC":
                table.add_row("Slope", self._create_field(field="slope"))
                table.add_row("Coupling", self.coupling)
                table.add_row("Holdoff", self._create_field(field="holdoff"))
                table.add_row("NoiseReject", self.noisereject)
            else:
                table.add_row("Level", self._create_field(field="level"))
                table.add_row("Slope", self._create_field(field="slope"))
                table.add_row("Coupling", self._create_field(field="coupling"))
                table.add_row("Holdoff", self._create_field(field="holdoff"))
                table.add_row("NoiseReject", self._create_field(field="noisereject"))
        else:
            table.add_row("NoiseReject", self._create_field(field="noisereject"))

        return Panel(table, title="Trigger")

    def _create_field(self, field):
        return super()._create_field(
            field=field, callback="app.edit_trigger('{:s}')".format(field)
        )

    async def edit_sweep(self):
        SWEEP_OPTIONS = ["AUTO", "NORM", "SING"]
        idx = SWEEP_OPTIONS.index(self.sweep) + 1
        idx = 0 if idx == len(SWEEP_OPTIONS) else idx
        self.update_oscope(sweep=SWEEP_OPTIONS[idx])

    async def edit_noisereject(self):
        self.update_oscope(noisereject=self.noisereject == "OFF")

    async def edit_mode(self):
        MODE_OPTIONS, MODE_NAMES = zip(*list(TRIGGER_MODES.items()))
        idx = MODE_NAMES.index(self.mode) + 1
        idx = 0 if idx == len(MODE_OPTIONS) else idx
        self.update_oscope(mode=MODE_OPTIONS[idx])

    async def edit_source(self):
        SOURCE_OPTIONS = ["CHAN1", "CHAN2", "CHAN3", "CHAN4", "AC"]
        idx = SOURCE_OPTIONS.index(self.source) + 1
        idx = 0 if idx == len(SOURCE_OPTIONS) else idx
        self.update_oscope(source=SOURCE_OPTIONS[idx])

    async def edit_coupling(self):
        COUPLING_OPTIONS = ["AC", "DC", "LFR", "HFR"]
        idx = COUPLING_OPTIONS.index(self.coupling) + 1
        idx = 0 if idx == len(COUPLING_OPTIONS) else idx
        self.update_oscope(coupling=COUPLING_OPTIONS[idx])

    async def edit_slope(self):
        SLOPE_OPTIONS = ["POS", "NEG", "RFAL"]
        idx = SLOPE_OPTIONS.index(self.slope) + 1
        idx = 0 if idx == len(SLOPE_OPTIONS) else idx
        self.update_oscope(slope=SLOPE_OPTIONS[idx])

    async def edit_level(self):
        self._edit_field("level")

    async def edit_holdoff(self):
        self._edit_field("holdoff")
