from typing import Optional

from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from si_prefix import si_format
from textual import events
from textual.keys import Keys
from textual.reactive import Reactive
from textual.widget import Widget

from rigol_ds1000z import Rigol_DS1000Z

CHANNEL_COLORS = {
    1: "bright_yellow",
    2: "bright_cyan",
    3: "plum2",
    4: "turquoise2",
}


def _float2si(raw, sigfigs, unit):
    si = si_format(raw, precision=sigfigs - 1).split()
    si_mag = "{:#.{:d}g}".format(float(si[0]), sigfigs).strip(".")
    si_unit = si[1] if len(si) == 2 else ""
    return si_mag + si_unit + unit


class Channel_TUI(Widget):

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

    highlight_field: Reactive[RenderableType] = Reactive("")
    editing_field: Reactive[RenderableType] = Reactive(None)
    editing_text: Reactive[RenderableType] = Reactive("")

    def __init__(self, oscope: Rigol_DS1000Z, n: int) -> None:
        super().__init__()
        self.oscope = oscope
        self.n = n
        self.label = "CH{:d}".format(n)
        self.update_oscope()

    async def on_mouse_move(self, event: events.MouseMove) -> None:
        field = event.style.meta.get("field")
        if self.highlight_field != field:
            self.highlight_field = field
            self._edit_field(None)

    async def on_key(self, event: events.Key) -> None:
        if self.editing_field is None:
            return

        if event.key == Keys.Escape:
            self._edit_field(None)
        elif event.key in (Keys.Backspace, Keys.ControlH):
            self.editing_text = self.editing_text[:-1]
        elif event.key in (Keys.Enter, Keys.Return, Keys.ControlM):
            if self.editing_field == "label":
                self.label = self.editing_text
                self._edit_field(None)
            else:
                try:
                    kwargs = {self.editing_field: float(self.editing_text)}
                except ValueError:
                    self._edit_field(None)
                else:
                    self.update_oscope(**kwargs)
                    self._edit_field(None)
        elif event.key != Keys.ControlAt:
            self.editing_text += event.key

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
        table.add_row("Volts/Div", self._create_field(field="vernier"))
        table.add_row("Unit", self._create_field(field="units"))
        table.add_row("Label", self._create_field(field="label"))

        return Panel(
            table,
            title="Channel {:d}".format(self.n),
            border_style=CHANNEL_COLORS[self.n],
        )

    def _create_field(self, field):
        editing = self.editing_field == field
        highlighted = editing or self.highlight_field == field
        value = self.editing_text if editing else getattr(self, field)
        style = "reverse" if highlighted else ""
        callback = "app.edit_channel({:d}, '{:s}')".format(self.n, field)
        text = Text(value.ljust(9), style).on(click=callback, meta={"field": field})
        return text

    def _edit_field(self, field):
        self.editing_field = field
        self.editing_text = ""
        self.app.editing = field is not None

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
