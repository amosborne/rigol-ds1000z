import argparse
import sys

import rigol_ds1000z.app.tui as tui
from rigol_ds1000z.src.oscope import Rigol_DS1000Z
from rigol_ds1000z.utils import process_display, process_waveform

parser = argparse.ArgumentParser(
    description=(
        "Save to file a display capture or waveform data from a Rigol DS1000Z series oscilloscope. "
        "Unless explicitly provided, the first valid VISA address will be used by default. "
        "If a display capture and waveform data are not requested, the user interface is opened. "
    ),
)

parser.add_argument(
    "-v", "--visa", type=str, metavar="RSRC", help="specify the VISA resource address"
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


def save_display(visa, filename):
    with Rigol_DS1000Z(visa) as oscope:
        display = oscope.display()
        process_display(display, filename=filename)


def save_waveform(visa, source, filename):
    with Rigol_DS1000Z(visa) as oscope:
        try:
            source = int(source)
        except ValueError:
            pass
        finally:
            waveform = oscope.waveform(source=source)
            process_waveform(waveform, filename=filename)


def main():
    args = parser.parse_args()

    if args.display is None and args.waveform is None:
        tui.run(args.visa)
        return

    if args.display is not None:
        save_display(args.visa, args.display)
    if args.waveform is not None:
        save_waveform(args.visa, *args.waveform)
