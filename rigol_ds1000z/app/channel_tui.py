from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from textual.reactive import Reactive

from rigol_ds1000z import Rigol_DS1000Z
from rigol_ds1000z.app.tablecontrol_tui import TableControl_TUI, _float2si

CHANNEL_COLORS = {
    1: "bright_yellow",
    2: "bright_cyan",
    3: "plum2",
    4: "turquoise2",
}


class Channel_TUI(TableControl_TUI):

    bwlimit: Reactive[RenderableType] = Reactive("")
    coupling: Reactive[RenderableType] = Reactive("")
    probe: Reactive[RenderableType] = Reactive("")
    invert: Reactive[RenderableType] = Reactive("")
    vernier: Reactive[RenderableType] = Reactive("")
    units: Reactive[RenderableType] = Reactive("")
    scale: Reactive[RenderableType] = Reactive("")
    offset: Reactive[RenderableType] = Reactive("")
    range: Reactive[RenderableType] = Reactive("")
    tcal: Reactive[RenderableType] = Reactive("")
    label: Reactive[RenderableType] = Reactive("")

    def __init__(self, oscope: Rigol_DS1000Z, n: int) -> None:
        self.n = n
        super().__init__(oscope)
        self.label = "CH{:d}".format(n)

    def update_oscope(self, **kwargs):
        channel = self.oscope.channel(self.n, **kwargs)
        self.bwlimit = "20M" if channel.bwlimit else "OFF"
        self.coupling = channel.coupling
        self.probe = "{:.2f}X".format(channel.probe).replace(".00", "")
        self.invert = "ON" if channel.invert else "OFF"
        self.vernier = "Fine" if channel.vernier else "Coarse"
        self.units = "[{:s}]".format(channel.units[0])
        self.scale = _float2si(channel.scale, sigfigs=3, unit=channel.units[0])
        self.offset = _float2si(channel.offset, sigfigs=4, unit=channel.units[0])
        self.range = _float2si(channel.range, sigfigs=3, unit=channel.units[0])
        self.tcal = _float2si(channel.tcal, sigfigs=3, unit="s")

    def render(self) -> RenderableType:
        table = Table(box=None, show_header=False)
        table.add_column(no_wrap=True, style=CHANNEL_COLORS[self.n])
        table.add_column(no_wrap=True, style=CHANNEL_COLORS[self.n])
        table.add_row("Scale", self._create_field(field="scale"))
        table.add_row("Offset", self._create_field(field="offset"))
        table.add_row("Range", self._create_field(field="range"))
        table.add_row("Delay", self._create_field(field="tcal"))
        table.add_row("Coupling", self._create_field(field="coupling"))
        table.add_row("BW Limit", self._create_field(field="bwlimit"))
        table.add_row("Probe", self._create_field(field="probe"))
        table.add_row("Invert", self._create_field(field="invert"))
        table.add_row("Volts/Div  ", self._create_field(field="vernier"))
        table.add_row("Unit", self._create_field(field="units"))
        table.add_row("Label", self._create_field(field="label"))

        return Panel(
            table,
            title="Channel {:d}".format(self.n),
            border_style=CHANNEL_COLORS[self.n],
        )

    def _create_field(self, field):
        return super()._create_field(
            field=field, callback="app.edit_channel({:d}, '{:s}')".format(self.n, field)
        )

    async def edit_scale(self):
        self._edit_field("scale")

    async def edit_offset(self):
        self._edit_field("offset")

    async def edit_range(self):
        self._edit_field("range")

    async def edit_tcal(self):
        self._edit_field("tcal")

    async def edit_probe(self):
        self._edit_field("probe")

    async def edit_coupling(self):
        COUPLING_OPTIONS = ["AC", "DC", "GND"]
        idx = COUPLING_OPTIONS.index(self.coupling) + 1
        idx = 0 if idx == len(COUPLING_OPTIONS) else idx
        self.update_oscope(coupling=COUPLING_OPTIONS[idx])

    async def edit_bwlimit(self):
        self.update_oscope(bwlimit=self.bwlimit == "OFF")

    async def edit_invert(self):
        self.update_oscope(invert=self.invert == "OFF")

    async def edit_vernier(self):
        self.update_oscope(vernier=self.vernier == "Coarse")

    async def edit_units(self):
        UNITS_OPTIONS = ["WATT", "AMP", "VOLT", "UNKN"]
        UNITS_OPTIONS_FIRST = [opt[0] for opt in UNITS_OPTIONS]
        idx = UNITS_OPTIONS_FIRST.index(self.units.strip("[]")) + 1
        idx = 0 if idx == len(UNITS_OPTIONS) else idx
        self.update_oscope(units=UNITS_OPTIONS[idx])

    async def edit_label(self):
        self._edit_field("label")
