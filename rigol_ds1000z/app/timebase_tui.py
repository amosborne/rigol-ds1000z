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


def _float2si(raw, sigfigs, unit):
    si = si_format(raw, precision=sigfigs - 1).split()
    si_mag = "{:#.{:d}g}".format(float(si[0]), sigfigs).strip(".")
    si_unit = si[1] if len(si) == 2 else ""
    return si_mag + si_unit + unit


class Timebase_TUI(Widget):

    mode: Reactive[RenderableType] = Reactive("")
    main_scale: Reactive[RenderableType] = Reactive("")
    main_offset: Reactive[RenderableType] = Reactive("")
    delay_enable: Reactive[RenderableType] = Reactive("")
    delay_scale: Reactive[RenderableType] = Reactive("")
    delay_offset: Reactive[RenderableType] = Reactive("")

    highlight_field: Reactive[RenderableType] = Reactive("")
    editing_field: Reactive[RenderableType] = Reactive(None)
    editing_text: Reactive[RenderableType] = Reactive("")

    def __init__(self, oscope: Rigol_DS1000Z) -> None:
        super().__init__()
        self.oscope = oscope
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
        table.add_row("Time Base", self._create_field(field="mode"))
        table.add_row("Delayed", self._create_field(field="delay_enable"))
        table.add_row("Scale", self._create_field(field="scale"))
        table.add_row("Offset", self._create_field(field="offset"))

        return Panel(table, title="Horizontal")

    def _create_field(self, field):
        if field in ("scale", "offset"):
            prefix = "main_" if self.delay_enable == "OFF" else "delay_"
            field = prefix + field

        editing = self.editing_field == field
        highlighted = editing or self.highlight_field == field

        value = self.editing_text if editing else getattr(self, field)
        style = "reverse" if highlighted else ""
        callback = "app.edit_timebase('{:s}')".format(field)
        text = Text(value.ljust(9), style).on(click=callback, meta={"field": field})
        return text

    def _edit_field(self, field):
        self.editing_field = field
        self.editing_text = ""
        self.app.editing = field is not None

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
