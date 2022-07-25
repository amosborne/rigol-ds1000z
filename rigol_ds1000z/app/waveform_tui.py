from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from textual.reactive import Reactive

from rigol_ds1000z.app.tablecontrol_tui import TableControl_TUI, _float2si


class Waveform_TUI(TableControl_TUI):

    source: Reactive[RenderableType] = Reactive("")
    mode: Reactive[RenderableType] = Reactive("")
    format: Reactive[RenderableType] = Reactive("")
    start: Reactive[RenderableType] = Reactive("")
    stop: Reactive[RenderableType] = Reactive("")

    def update_oscope(self, **kwargs):
        waveform = self.oscope.waveform(**kwargs)
        self.source = (
            waveform.source
            if waveform.source == "MATH"
            else "CHAN" + str(waveform.source)
        )
        self.mode = waveform.mode
        self.format = waveform.format
        self.start = str(waveform.start)
        self.stop = str(waveform.stop)

    def render(self) -> RenderableType:
        table = Table(box=None, show_header=False)
        table.add_column(no_wrap=True)
        table.add_column(no_wrap=True)
        table.add_row("Source", self._create_field(field="source"))
        table.add_row("Mode", self._create_field(field="mode"))
        table.add_row("Format     ", self._create_field(field="format"))
        table.add_row("Start", self._create_field(field="start"))
        table.add_row("Stop", self._create_field(field="stop"))

        return Panel(table, title="Waveform")

    def _create_field(self, field):
        return super()._create_field(
            field=field, callback="app.edit_waveform('{:s}')".format(field)
        )

    async def edit_source(self):
        SOURCE_OPTIONS = ["CHAN1", "CHAN2", "CHAN3", "CHAN4", "MATH"]
        idx = SOURCE_OPTIONS.index(self.source) + 1
        idx = 0 if idx == len(SOURCE_OPTIONS) else idx
        self.update_oscope(source=SOURCE_OPTIONS[idx])

    async def edit_mode(self):
        MODE_OPTIONS = ["NORM", "MAX", "RAW"]
        idx = MODE_OPTIONS.index(self.mode) + 1
        idx = 0 if idx == len(MODE_OPTIONS) else idx
        self.update_oscope(mode=MODE_OPTIONS[idx])

    async def edit_format(self):
        FORMAT_OPTIONS = ["WORD", "BYTE", "ASC"]
        idx = FORMAT_OPTIONS.index(self.format) + 1
        idx = 0 if idx == len(FORMAT_OPTIONS) else idx
        self.update_oscope(format=FORMAT_OPTIONS[idx])

    async def edit_start(self):
        self._edit_field("start", formatter=int)

    async def edit_stop(self):
        self._edit_field("stop", formatter=int)
