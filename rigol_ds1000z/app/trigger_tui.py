from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from textual.reactive import Reactive

from rigol_ds1000z import Rigol_DS1000Z
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
    nreject: Reactive[RenderableType] = Reactive("")
    mode: Reactive[RenderableType] = Reactive("")
    holdoff: Reactive[RenderableType] = Reactive("")
    coupling: Reactive[RenderableType] = Reactive("")
    edge_source: Reactive[RenderableType] = Reactive("")
    edge_slope: Reactive[RenderableType] = Reactive("")
    edge_level: Reactive[RenderableType] = Reactive("")

    def __init__(self, oscope: Rigol_DS1000Z, channels) -> None:
        self.channels = channels
        super().__init__(oscope)

    def update_oscope(self, **kwargs):
        trigger = self.oscope.trigger(**kwargs)
        self.status = trigger.status
        self.sweep = trigger.sweep
        self.nreject = "ON" if trigger.nreject else "OFF"
        self.mode = TRIGGER_MODES[trigger.mode]
        self.holdoff = (
            _float2si(trigger.holdoff, sigfigs=3, unit="s")
            if trigger.mode == "EDGE"
            else None
        )
        self.coupling = trigger.coupling if trigger.mode == "EDGE" else None
        self.edge_slope = trigger.edge_slope if trigger.mode == "EDGE" else None
        self.edge_level = (
            _float2si(
                trigger.edge_level,
                sigfigs=3,
                unit=self.channels[trigger.edge_source - 1].units[1],
            )
            if trigger.mode == "EDGE" and not trigger.edge_source == "AC"
            else None
        )

        if trigger.mode == "EDGE":
            if isinstance(trigger.edge_source, int):
                self.edge_source = "CHAN{:d}".format(trigger.edge_source)
            else:
                self.edge_source = trigger.edge_source
        else:
            self.edge_source = None

    def render(self) -> RenderableType:
        table = Table(box=None, show_header=False)
        table.add_column(no_wrap=True)
        table.add_column(no_wrap=True)
        table.add_row("Status", self.status)
        table.add_row("Mode", self._create_field(field="sweep"))
        table.add_row("Type", self._create_field(field="mode"))

        if self.mode == "Edge":
            table.add_row("Source", self._create_field(field="edge_source"))
            if self.edge_source == "AC":
                table.add_row("Slope", self._create_field(field="edge_slope"))
                table.add_row("Coupling", self.coupling)
                table.add_row("Holdoff", self._create_field(field="holdoff"))
                table.add_row("NoiseReject", self.nreject)
            else:
                table.add_row("Level", self._create_field(field="edge_level"))
                table.add_row("Slope", self._create_field(field="edge_slope"))
                table.add_row("Coupling", self._create_field(field="coupling"))
                table.add_row("Holdoff", self._create_field(field="holdoff"))
                table.add_row("NoiseReject", self._create_field(field="nreject"))
        else:
            table.add_row("NoiseReject", self._create_field(field="nreject"))

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

    async def edit_nreject(self):
        self.update_oscope(nreject=self.nreject == "OFF")

    async def edit_mode(self):
        MODE_OPTIONS, MODE_NAMES = zip(*list(TRIGGER_MODES.items()))
        idx = MODE_NAMES.index(self.mode) + 1
        idx = 0 if idx == len(MODE_OPTIONS) else idx
        self.update_oscope(mode=MODE_OPTIONS[idx])

    async def edit_edge_source(self):
        SOURCE_OPTIONS = ["CHAN1", "CHAN2", "CHAN3", "CHAN4", "AC"]
        idx = SOURCE_OPTIONS.index(self.edge_source) + 1
        idx = 0 if idx == len(SOURCE_OPTIONS) else idx
        self.update_oscope(edge_source=SOURCE_OPTIONS[idx])

    async def edit_coupling(self):
        COUPLING_OPTIONS = ["AC", "DC", "LFR", "HFR"]
        idx = COUPLING_OPTIONS.index(self.coupling) + 1
        idx = 0 if idx == len(COUPLING_OPTIONS) else idx
        self.update_oscope(coupling=COUPLING_OPTIONS[idx])

    async def edit_edge_slope(self):
        SLOPE_OPTIONS = ["POS", "NEG", "RFAL"]
        idx = SLOPE_OPTIONS.index(self.edge_slope) + 1
        idx = 0 if idx == len(SLOPE_OPTIONS) else idx
        self.update_oscope(edge_slope=SLOPE_OPTIONS[idx])

    async def edit_edge_level(self):
        self._edit_field("edge_level")

    async def edit_holdoff(self):
        self._edit_field("holdoff")
