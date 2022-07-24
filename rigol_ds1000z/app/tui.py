from textual import events
from textual.app import App
from textual.widgets import Footer, Placeholder

from rigol_ds1000z import Rigol_DS1000Z, find_visa
from rigol_ds1000z.app.channel_tui import Channel_TUI
from rigol_ds1000z.app.timebase_tui import Timebase_TUI


def disable_while_editing(func):
    def wrapper(*args, **kwargs):
        if not args[0].editing:
            return func(*args, **kwargs)

    return wrapper


class Rigol_DS100Z_TUI(App):
    async def on_load(self, event: events.Load) -> None:
        await self.bind("q", "quit", "Quit")
        await self.bind("r", "refresh", "Refresh")
        await self.bind("1", "channel1", "Ch1")
        await self.bind("2", "channel2", "Ch2")
        await self.bind("3", "channel3", "Ch3")
        await self.bind("4", "channel4", "Ch4")
        await self.bind("c", "clear", "Clear")
        await self.bind("a", "autoscale", "Auto")
        await self.bind("s", "runstop", "Run/Stop")
        await self.bind("i", "single", "Single")
        await self.bind("f", "force", "Force")
        await self.bind("d", "display", "Display")
        await self.bind("w", "waveform", "Waveform")

        self.oscope = Rigol_DS1000Z(visa=find_visa()).open()
        self.editing = False

    async def on_mount(self, event: events.Mount) -> None:
        grid = await self.view.dock_grid()

        grid.add_column(name="ch1-col")
        grid.add_column(name="ch2-col")
        grid.add_column(name="ch3-col")
        grid.add_column(name="ch4-col")

        grid.add_row(name="horiz-row")
        grid.add_row(name="vert-row", fraction=0, min_size=13)
        grid.add_row(name="console-row", fraction=0, min_size=3)
        grid.add_row(name="footer-row", fraction=0, min_size=1)

        grid.add_areas(display="ch1-col,horiz-row")
        grid.add_areas(waveform="ch2-col,horiz-row")
        grid.add_areas(timebase="ch3-col,horiz-row")
        grid.add_areas(trigger="ch4-col,horiz-row")
        grid.add_areas(vert_ch1="ch1-col,vert-row")
        grid.add_areas(vert_ch2="ch2-col,vert-row")
        grid.add_areas(vert_ch3="ch3-col,vert-row")
        grid.add_areas(vert_ch4="ch4-col,vert-row")
        grid.add_areas(console="ch1-col-start|ch4-col-end,console-row")
        grid.add_areas(footer="ch1-col-start|ch4-col-end,footer-row")

        self.channels = [Channel_TUI(self.oscope, n=x + 1) for x in range(4)]
        self.timebase = Timebase_TUI(self.oscope)

        grid.place(
            display=Placeholder(name="DISPLAY"),
            waveform=Placeholder(name="WAVEFORM"),
            timebase=self.timebase,
            trigger=Placeholder(name="TRIGGER"),
            vert_ch1=self.channels[0],
            vert_ch2=self.channels[1],
            vert_ch3=self.channels[2],
            vert_ch4=self.channels[3],
            console=Placeholder(name="CONSOLE"),
            footer=Footer(),
        )

    @disable_while_editing
    async def action_refresh(self) -> None:
        # TODO: update all widgets with latest settings
        pass

    @disable_while_editing
    async def action_quit(self) -> None:
        self.oscope.close()
        await super().action_quit()

    @disable_while_editing
    async def action_channel1(self) -> None:
        is_active = not self.oscope.channel(n=1).display
        self.oscope.channel(n=1, display=is_active)

    @disable_while_editing
    async def action_channel2(self) -> None:
        is_active = not self.oscope.channel(n=2).display
        self.oscope.channel(n=2, display=is_active)

    @disable_while_editing
    async def action_channel3(self) -> None:
        is_active = not self.oscope.channel(n=3).display
        self.oscope.channel(n=3, display=is_active)

    @disable_while_editing
    async def action_channel4(self) -> None:
        is_active = not self.oscope.channel(n=4).display
        self.oscope.channel(n=4, display=is_active)

    @disable_while_editing
    async def action_clear(self) -> None:
        self.oscope.clear()

    @disable_while_editing
    async def action_autoscale(self) -> None:
        self.oscope.autoscale()

    @disable_while_editing
    async def action_runstop(self) -> None:
        # TODO: check trigger status, toggle run/stop
        pass

    @disable_while_editing
    async def action_single(self) -> None:
        self.oscope.single()

    @disable_while_editing
    async def action_force(self) -> None:
        self.oscope.tforce()

    @disable_while_editing
    async def action_display(self) -> None:
        # TODO: capture the oscope display and screenshot the tui
        pass

    @disable_while_editing
    async def action_waveform(self) -> None:
        # TODO: save all the waveforms with active channel displays
        pass

    @disable_while_editing
    async def action_edit_channel(self, channel: int, field: str) -> None:
        await getattr(self.channels[channel - 1], "edit_{:s}".format(field))()

    @disable_while_editing
    async def action_edit_timebase(self, field: str) -> None:
        await getattr(self.timebase, "edit_{:s}".format(field))()


def run():
    Rigol_DS100Z_TUI.run(title="rigol-ds1000z")
