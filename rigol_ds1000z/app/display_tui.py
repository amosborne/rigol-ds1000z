from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from si_prefix import si_format
from textual.reactive import Reactive

from rigol_ds1000z.app.tablecontrol_tui import TableControl_TUI, _float2si


class Display_TUI(TableControl_TUI):

    type: Reactive[RenderableType] = Reactive("")
    grading_time: Reactive[RenderableType] = Reactive("")
    wave_brightness: Reactive[RenderableType] = Reactive("")
    grid: Reactive[RenderableType] = Reactive("")
    grid_brightness: Reactive[RenderableType] = Reactive("")

    def update_oscope(self, **kwargs):
        display = self.oscope.display(**kwargs)
        self.type = "Vector" if display.type == "VECT" else "Dots"
        self.wave_brightness = "{:d}%".format(display.wave_brightness)
        self.grid = display.grid
        self.grid_brightness = "{:d}%".format(display.grid_brightness)

        if isinstance(display.grading_time, str):
            self.grading_time = "Min" if display.grading_time == "MIN" else "Infinite"
        else:
            si = si_format(display.grading_time, precision=0).split()
            si_unit = si[1] if len(si) == 2 else ""
            self.grading_time = si[0] + si_unit + "s"

    def render(self) -> RenderableType:
        table = Table(box=None, show_header=False)
        table.add_column(no_wrap=True)
        table.add_column(no_wrap=True)
        table.add_row("Type", self._create_field(field="type"))
        table.add_row("Persis Time", self._create_field(field="grading_time"))
        table.add_row("Intensity", self._create_field(field="wave_brightness"))
        table.add_row("Grid", self._create_field(field="grid"))
        table.add_row("Brightness", self._create_field(field="grid_brightness"))

        return Panel(table, title="Display")

    def _create_field(self, field):
        return super()._create_field(
            field=field, callback="app.edit_display('{:s}')".format(field)
        )

    async def edit_type(self):
        self.update_oscope(type="VECT" if self.type == "Dots" else "DOTS")

    async def edit_grading_time(self):
        def grading_time_formatter(time):
            try:
                ftime = float(time)
            except ValueError:
                return time
            else:
                return "INF" if ftime == float("inf") else ftime

        self._edit_field("grading_time", formatter=grading_time_formatter)

    async def edit_wave_brightness(self):
        self._edit_field("wave_brightness", formatter=int)

    async def edit_grid(self):
        GRID_OPTIONS = ["FULL", "HALF", "NONE"]
        idx = GRID_OPTIONS.index(self.grid) + 1
        idx = 0 if idx == len(GRID_OPTIONS) else idx
        self.update_oscope(grid=GRID_OPTIONS[idx])

    async def edit_grid_brightness(self):
        self._edit_field("grid_brightness", formatter=int)
