from abc import ABC, abstractmethod
from typing import Optional

from rich.console import RenderableType
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


class TableControl_TUI(Widget, ABC):

    highlight_field: Reactive[RenderableType] = Reactive("")
    editing_field: Reactive[RenderableType] = Reactive(None)
    editing_text: Reactive[RenderableType] = Reactive("")
    editing_formatter = None

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
                kwargs = {self.editing_field: self.editing_formatter(self.editing_text)}
            except ValueError:
                self._edit_field(None)
            else:
                self.update_oscope(**kwargs)
                self._edit_field(None)
        elif event.key != Keys.ControlAt:
            self.editing_text += event.key

    def _create_field(self, field: str, callback: str) -> Text:
        editing = self.editing_field == field
        highlighted = editing or self.highlight_field == field

        value = self.editing_text if editing else getattr(self, field)
        style = "reverse" if highlighted else ""
        text = Text(value.ljust(9), style).on(click=callback, meta={"field": field})
        return text

    def _edit_field(self, field: Optional[str], formatter=float) -> None:
        self.editing_field = field
        self.editing_text = ""
        self.editing_formatter = formatter
        self.app.editing = field is not None

    @abstractmethod
    def update_oscope(self, **kwargs) -> None:
        pass
