import argparse
import sys

import rigol_ds1000z.app.tui as tui

from rigol_ds1000z import Rigol_DS1000Z, find_visa, process_display, process_waveform

parser = argparse.ArgumentParser(
    description=(
        "Save to file a display capture or waveform data from a Rigol DS1000Z series "
        "oscilloscope. The first valid VISA address identified is utilized by default."
    ),
)

parser.add_argument(
    "-d",
    "--display",
    type=str,
    metavar="FILE",
    help="save display capture, file extension .png is recommended",
)

parser.add_argument(
    "-w",
    "--waveform",
    nargs=2,
    type=str,
    metavar=("SRC", "FILE"),
    help="save waveform data, file extension .csv is recommended",
)


def save_display(filename):
    with Rigol_DS1000Z(find_visa()) as oscope:
        display = oscope.display()
        process_display(display, filename=filename)


def save_waveform(source, filename):
    with Rigol_DS1000Z(find_visa()) as oscope:
        try:
            source = int(source)
        except ValueError:
            pass
        finally:
            waveform = oscope.waveform(source=source)
            process_waveform(waveform, filename=filename)


def main():
    if not len(sys.argv) > 1:
        tui.run()
        return

    args = parser.parse_args()
    if args.display is not None:
        save_display(args.display)
    if args.waveform is not None:
        save_waveform(*args.waveform)
