from typing import Optional

from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from si_prefix import si_format
from textual.reactive import Reactive
from textual.widget import Widget

from rigol_ds1000z import Rigol_DS1000Z

CHANNEL_COLORS = {
    1: "bright_yellow",
    2: "bright_cyan",
    3: "bright_magenta",
    4: "bright_blue",
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
    vrange: Reactive[RenderableType] = Reactive("")
    tcal: Reactive[RenderableType] = Reactive("")

    def __init__(self, oscope: Rigol_DS1000Z, n: int) -> None:
        super().__init__()
        self.oscope = oscope
        self.n = n

        channel = oscope.channel(n)
        self.bwlimit = "20M" if channel.bwlimit else "OFF"
        self.coupling = channel.coupling
        self.probe = "{:.2f}X".format(channel.probe).replace(".00", "")
        self.invert = "ON" if channel.invert else "OFF"
        self.vernier = "Fine" if channel.vernier else "Coarse"
        self.units = "[{:s}]".format(channel.units[0])
        self.scale = _float2si(channel.scale, sigfigs=3, unit=channel.units[0])
        self.offset = _float2si(channel.offset, sigfigs=4, unit=channel.units[0])
        self.vrange = _float2si(channel.range, sigfigs=3, unit=channel.units[0])
        self.tcal = _float2si(channel.tcal, sigfigs=3, unit="s")

    def render(self) -> RenderableType:
        table = Table(box=None, show_header=False)
        table.add_column(no_wrap=True, style=CHANNEL_COLORS[self.n])
        table.add_column(no_wrap=True, style=CHANNEL_COLORS[self.n])
        table.add_row("Scale", self.scale)
        table.add_row("Offset", self.offset)
        table.add_row("Range", self.vrange)
        table.add_row("Delay", self.tcal)
        table.add_row("Coupling", self.coupling)
        table.add_row("BW Limit", self.bwlimit)
        table.add_row("Probe", self.probe)
        table.add_row("Invert", self.invert)
        table.add_row("Volts/Div", self.vernier)
        table.add_row("Unit", self.units)

        return Panel(
            table,
            title="Channel {:d}".format(self.n),
            border_style=CHANNEL_COLORS[self.n],
        )
