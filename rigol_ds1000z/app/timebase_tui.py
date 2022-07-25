from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from textual.reactive import Reactive

from rigol_ds1000z.app.tablecontrol_tui import TableControl_TUI, _float2si


class Timebase_TUI(TableControl_TUI):

    mode: Reactive[RenderableType] = Reactive("")
    main_scale: Reactive[RenderableType] = Reactive("")
    main_offset: Reactive[RenderableType] = Reactive("")
    delay_enable: Reactive[RenderableType] = Reactive("")
    delay_scale: Reactive[RenderableType] = Reactive("")
    delay_offset: Reactive[RenderableType] = Reactive("")

    def update_oscope(self, **kwargs):
        timebase = self.oscope.timebase(**kwargs)
        self.mode = "YT" if timebase.mode == "MAIN" else timebase.mode
        self.main_scale = _float2si(timebase.main_scale, sigfigs=3, unit="s")
        self.main_offset = _float2si(timebase.main_offset, sigfigs=3, unit="s")
        self.delay_enable = "ON" if timebase.delay_enable else "OFF"
        self.delay_scale = _float2si(timebase.delay_scale, sigfigs=3, unit="s")
        self.delay_offset = _float2si(timebase.delay_offset, sigfigs=3, unit="s")

    def render(self) -> RenderableType:
        table = Table(box=None, show_header=False)
        table.add_column(no_wrap=True)
        table.add_column(no_wrap=True)
        table.add_row("Time Base  ", self._create_field(field="mode"))
        table.add_row("Delayed", self._create_field(field="delay_enable"))
        table.add_row("Scale", self._create_field(field="scale"))
        table.add_row("Offset", self._create_field(field="offset"))

        return Panel(table, title="Horizontal")

    def _create_field(self, field):
        if field in ("scale", "offset"):
            prefix = "main_" if self.delay_enable == "OFF" else "delay_"
            field = prefix + field

        return super()._create_field(
            field=field, callback="app.edit_timebase('{:s}')".format(field)
        )

    async def edit_mode(self):
        MODE_OPTIONS = ["MAIN", "XY", "ROLL"]
        MODE_NAMES = ["YT", "XY", "ROLL"]
        idx = MODE_NAMES.index(self.mode) + 1
        idx = 0 if idx == len(MODE_OPTIONS) else idx
        self.update_oscope(mode=MODE_OPTIONS[idx])

    async def edit_main_scale(self):
        self._edit_field("main_scale")

    async def edit_main_offset(self):
        self._edit_field("main_offset")

    async def edit_delay_enable(self):
        self.update_oscope(delay_enable=self.delay_enable == "OFF")

    async def edit_delay_scale(self):
        self._edit_field("delay_scale")

    async def edit_delay_offset(self):
        self._edit_field("delay_offset")
