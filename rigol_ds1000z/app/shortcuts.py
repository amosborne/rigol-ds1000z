from rich.console import RenderableType
from rich.text import Text
from textual import events
from textual.reactive import Reactive
from textual.widget import Widget

from rigol_ds1000z.app.channel_tui import CHANNEL_COLORS


class Shortcuts(Widget):
    highlight_key: Reactive[RenderableType] = Reactive("")

    async def on_mouse_move(self, event: events.MouseMove) -> None:
        self.highlight_key = event.style.meta.get("key")

    async def on_leave(self, event: events.Leave) -> None:
        self.highlight_key = ""

    def _simple_button(self, key, name) -> RenderableType:
        return Text.assemble(
            (
                " {:s} ".format(key.upper()),
                "reverse" if self.highlight_key == key else "default on default",
            ),
            (" {:s} ".format(name), "white on dark_green"),
            meta={"key": key, "@click": "app.press('{:s}')".format(key)},
        )

    def _status_button(self, key, name, style, status) -> RenderableType:
        if status != (self.highlight_key == key):
            style = "reverse {:s}".format(style)

        return Text.assemble(
            (" {:s} ".format(key.upper()), style),
            (" {:s} ".format(name), "white on dark_green"),
            meta={"key": key, "@click": "app.press('{:s}')".format(key)},
        )


class Shortcuts_Header(Shortcuts):
    runstop: Reactive[RenderableType] = Reactive(True)
    singlestatus: Reactive[RenderableType] = Reactive(False)

    def render(self) -> RenderableType:
        runstop_style = (
            "black on sea_green2"
            if self.runstop != (self.highlight_key == "s")
            else "black on red1"
        )
        runstop_text = Text.assemble(
            (" S ", runstop_style),
            (" Run/Stop ", "white on dark_green"),
            meta={"key": "s", "@click": "app.press('s')"},
        )

        single_style = (
            "black on sea_green2"
            if self.singlestatus != (self.highlight_key == "i")
            else "default on default"
        )
        single_text = Text.assemble(
            (" I ", single_style),
            (" Single ", "white on dark_green"),
            meta={"key": "i", "@click": "app.press('i')"},
        )

        return (
            self._simple_button("q", "Quit")
            + self._simple_button("r", "Refresh")
            + self._simple_button("d", "Display")
            + self._simple_button("w", "Waveform")
            + self._simple_button("c", "Clear")
            + self._simple_button("a", "Autoscale")
            + runstop_text
            + single_text
            + self._simple_button("f", "Force")
        )


class Shortcuts_Footer(Shortcuts):
    channel1: Reactive[RenderableType] = Reactive(False)
    channel2: Reactive[RenderableType] = Reactive(False)
    channel3: Reactive[RenderableType] = Reactive(False)
    channel4: Reactive[RenderableType] = Reactive(False)

    def render(self) -> RenderableType:
        return (
            self._status_button("1", "Ch1", CHANNEL_COLORS[1], self.channel1)
            + self._status_button("2", "Ch2", CHANNEL_COLORS[2], self.channel2)
            + self._status_button("3", "Ch3", CHANNEL_COLORS[3], self.channel3)
            + self._status_button("4", "Ch4", CHANNEL_COLORS[4], self.channel4)
        )
