import os
from tkinter import Tk
from tkinter.filedialog import asksaveasfilename

from rich.console import Console
from textual import events
from textual.app import App

from rigol_ds1000z import Rigol_DS1000Z, process_display, process_waveform
from rigol_ds1000z.app.channel_tui import Channel_TUI
from rigol_ds1000z.app.display_tui import Display_TUI
from rigol_ds1000z.app.shortcuts import Shortcuts_Footer, Shortcuts_Header
from rigol_ds1000z.app.timebase_tui import Timebase_TUI
from rigol_ds1000z.app.trigger_tui import Trigger_TUI
from rigol_ds1000z.app.waveform_tui import Waveform_TUI


def disable_while_editing(func):
    def wrapper(*args, **kwargs):
        if not args[0].editing:
            return func(*args, **kwargs)

    return wrapper


class Rigol_DS100Z_TUI(App):
    def __init__(self, *args, visa=None, **kwargs):
        self.oscope = Rigol_DS1000Z(visa).open()
        super().__init__()

    async def on_load(self, event: events.Load) -> None:
        await self.bind("q", "quit")
        await self.bind("r", "refresh")
        await self.bind("1", "channel1")
        await self.bind("2", "channel2")
        await self.bind("3", "channel3")
        await self.bind("4", "channel4")
        await self.bind("c", "clear")
        await self.bind("a", "autoscale")
        await self.bind("s", "runstop")
        await self.bind("i", "single")
        await self.bind("f", "force")
        await self.bind("d", "display")
        await self.bind("w", "waveform")

        self.editing = False

    async def on_mount(self, event: events.Mount) -> None:
        grid = await self.view.dock_grid()

        grid.add_column(name="ch1-col")
        grid.add_column(name="ch2-col")
        grid.add_column(name="ch3-col")
        grid.add_column(name="ch4-col")

        grid.add_row(name="header-row")
        grid.add_row(name="horiz-row", min_size=11, max_size=11)
        grid.add_row(name="vert-row", min_size=13, max_size=13)
        grid.add_row(name="footer-row")

        grid.add_areas(header="ch1-col-start|ch4-col-end,header-row")
        grid.add_areas(display="ch1-col,horiz-row")
        grid.add_areas(waveform="ch2-col,horiz-row")
        grid.add_areas(timebase="ch3-col,horiz-row")
        grid.add_areas(trigger="ch4-col,horiz-row")
        grid.add_areas(vert_ch1="ch1-col,vert-row")
        grid.add_areas(vert_ch2="ch2-col,vert-row")
        grid.add_areas(vert_ch3="ch3-col,vert-row")
        grid.add_areas(vert_ch4="ch4-col,vert-row")
        grid.add_areas(footer="ch1-col-start|ch4-col-end,footer-row")

        self.header = Shortcuts_Header()
        self.channels = [Channel_TUI(self.oscope, n=x + 1) for x in range(4)]
        self.timebase = Timebase_TUI(self.oscope)
        self.oscopedisplay = Display_TUI(self.oscope)
        self.waveform = Waveform_TUI(self.oscope)
        self.trigger = Trigger_TUI(self.oscope, channels=self.channels)
        self.footer = Shortcuts_Footer()

        grid.place(
            header=self.header,
            display=self.oscopedisplay,
            waveform=self.waveform,
            timebase=self.timebase,
            trigger=self.trigger,
            vert_ch1=self.channels[0],
            vert_ch2=self.channels[1],
            vert_ch3=self.channels[2],
            vert_ch4=self.channels[3],
            footer=self.footer,
        )

        await self.action_refresh()

    @disable_while_editing
    async def action_refresh(self) -> None:
        [channel.update_oscope() for channel in self.channels]
        self.timebase.update_oscope()
        self.waveform.update_oscope()
        self.oscopedisplay.update_oscope()
        self.trigger.update_oscope()
        self.footer.channel1 = self.oscope.channel(n=1).display
        self.footer.channel2 = self.oscope.channel(n=2).display
        self.footer.channel3 = self.oscope.channel(n=3).display
        self.footer.channel4 = self.oscope.channel(n=4).display
        self.header.runstop = self.oscope.trigger().status != "STOP"
        self.header.singlestatus = self.oscope.trigger().status == "WAIT"

    @disable_while_editing
    async def action_quit(self) -> None:
        self.oscope.close()
        await super().action_quit()

    @disable_while_editing
    async def action_channel1(self) -> None:
        is_active = not self.oscope.channel(n=1).display
        self.footer.channel1 = is_active
        self.channels[0].update_oscope(display=is_active)

    @disable_while_editing
    async def action_channel2(self) -> None:
        is_active = not self.oscope.channel(n=2).display
        self.footer.channel2 = is_active
        self.channels[1].update_oscope(display=is_active)

    @disable_while_editing
    async def action_channel3(self) -> None:
        is_active = not self.oscope.channel(n=3).display
        self.footer.channel3 = is_active
        self.channels[2].update_oscope(display=is_active)

    @disable_while_editing
    async def action_channel4(self) -> None:
        is_active = not self.oscope.channel(n=4).display
        self.footer.channel4 = is_active
        self.channels[3].update_oscope(display=is_active)

    @disable_while_editing
    async def action_clear(self) -> None:
        self.oscope.clear()

    @disable_while_editing
    async def action_autoscale(self) -> None:
        self.oscope.autoscale()
        await self.action_refresh()

    @disable_while_editing
    async def action_runstop(self) -> None:
        if self.trigger.status == "STOP":
            self.oscope.run()
        else:
            self.oscope.stop()

        await self.action_refresh()

    @disable_while_editing
    async def action_single(self) -> None:
        self.oscope.single()
        await self.action_refresh()

    @disable_while_editing
    async def action_force(self) -> None:
        self.oscope.tforce()
        await self.action_refresh()

    @disable_while_editing
    async def action_display(self) -> None:
        await self.action_refresh()
        Tk().withdraw()
        filename = asksaveasfilename(
            title="Save Display As...",
            initialdir=os.getcwd(),
            initialfile="display.png",
            filetypes=[(".png", "*.png")],
            defaultextension="png",
        )
        if filename:
            process_display(self.oscope.display(), filename=filename)

            console = Console(
                width=self.console.width, height=self.console.height, record=True
            )
            console.print(self.view)
            console.save_svg(
                os.path.splitext(filename)[0] + "_softpanel.svg", title="rigol-ds1000z"
            )
            self.refresh()

    @disable_while_editing
    async def action_waveform(self) -> None:
        Tk().withdraw()
        filename = asksaveasfilename(
            title="Save Waveform As...",
            initialdir=os.getcwd(),
            initialfile="waveform.csv",
            filetypes=[("CSV UTF-8 (Comma delimited)", "*.csv")],
            defaultextension="csv",
        )
        if filename:
            process_waveform(self.oscope.waveform(), filename=filename)

    @disable_while_editing
    async def action_edit_channel(self, channel: int, field: str) -> None:
        await getattr(self.channels[channel - 1], "edit_{:s}".format(field))()
        self.trigger.update_oscope()

    @disable_while_editing
    async def action_edit_timebase(self, field: str) -> None:
        await getattr(self.timebase, "edit_{:s}".format(field))()

    @disable_while_editing
    async def action_edit_waveform(self, field: str) -> None:
        await getattr(self.waveform, "edit_{:s}".format(field))()

    @disable_while_editing
    async def action_edit_display(self, field: str) -> None:
        await getattr(self.oscopedisplay, "edit_{:s}".format(field))()

    @disable_while_editing
    async def action_edit_trigger(self, field: str) -> None:
        await getattr(self.trigger, "edit_{:s}".format(field))()


def run(visa):
    if os.name == "nt":  # resize the terminal on Windows
        os.system("mode con: cols=108 lines=26")
    Rigol_DS100Z_TUI.run(visa=visa, title="rigol-ds1000z")
