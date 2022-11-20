# rigol-ds1000z

In addition to this README, I have also written a [blog post](https://www.osborneee.com/rigol-ds1000z/) about this application.

## An oscilloscope user interface that never leaves the terminal.

![RigolDS1000Z_StillScreen](https://github.com/amosborne/rigol-ds1000z/raw/main/docs/rigol_ds1000z.png)

![Rigol_DS1000Z_Animated](https://github.com/amosborne/rigol-ds1000z/raw/main/docs/rigol_ds1000z.gif)

## A simple command line tool for grabbing data and pictures.

```shell
rigol-ds1000z --help
rigol-ds1000z --visa rsrc --display path/to/file.png
rigol-ds1000z --visa rsrc --waveform src path/to/file.csv 
```

Unless a VISA resource is specified with the `--visa` argument, the CLI will search for a Rigol DS1000Z series oscilloscope and connect to the first one it finds.

The CLI can capture and save to file an image of the display (`--display`) or the waveform data of the specified source channel (`--waveform`).

## A compact Python interface for automating test procedures.

See the provided [examples](https://github.com/amosborne/rigol-ds1000z/tree/main/examples) and read the [documentation.](https://amosborne.github.io/rigol-ds1000z/)

```python
from rigol_ds1000z import Rigol_DS1000Z
from rigol_ds1000z import process_display, process_waveform
from time import sleep

with Rigol_DS1000Z() as oscope:
    # reset to defaults and print the IEEE 488.2 instrument identifier
    ieee = oscope.ieee(rst=True)
    print(ieee.idn)

    # configure channels 1 and 2, the timebase, and the trigger
    channel1 = oscope.channel(1, probe=1, coupling="AC", offset=3.0, scale=2)
    channel2 = oscope.channel(2, probe=1, scale=1, display=True)
    timebase = oscope.timebase(main_scale=200e-6)
    trigger = oscope.trigger(mode="EDGE", source=2, coupling="DC", level=1.5)

    # send an SCPI commands to setup the math channel
    oscope.write(":MATH:DISPlay ON")
    oscope.write(":MATH:OPER SUBT")
    oscope.write(":MATH:SOUR2 CHAN2")
    oscope.write(":MATH:SCAL 5")
    oscope.write(":MATH:OFFS -10")

    # wait three seconds then single trigger
    sleep(3)
    oscope.single()

    # capture the display image
    display = oscope.display()
    process_display(display, show=True)

    # plot the channel 1 waveform data
    waveform = oscope.waveform(source=1)
    process_waveform(waveform, show=True)

```

## Installation instructions and notes to the user.

`pip install rigol-ds1000z`

Available on [PyPI](https://pypi.org/project/rigol-ds1000z/). This package uses [PyVISA](https://pyvisa.readthedocs.io/en/1.12.0/introduction/getting.html) to communicate with the oscilloscope. The user will have to install some VISA backend library for their operating system such as National Instrument's VISA library or libusb (this package supports both the "@ivi" and "@py" PyVISA backends transparently).

This software has been tested on Windows (Command Prompt and PowerShell), although it should be possible to run in other shells and/or operating systems. For best visual performance, a default of white text on a black background is recommended.

The software does insert some sleep time on specific commands (such as reset and autoscale) to ensure fluid operation of the oscilloscope. The user may find that they require additional downtime after certain command sequences.

## Software development and references.

[Rigol DS1000Z programming manual.](https://beyondmeasure.rigoltech.com/acton/attachment/1579/f-0386/1/-/-/-/-/DS1000Z_Programming%20Guide_EN.pdf)

| Command Category | Coverage |
| --- | --- |
| AUToscale, etc. | YES |
| ACQuire | no |
| CALibrate | no |
| CHANnel | YES |
| CURSor | no |
| DECoder | no |
| DISPlay | YES |
| ETABle | no |
| FUNCtion | no |
| IEEE 488.2 | YES |
| LA | no |
| LAN | no |
| MATH | no |
| MASK | no |
| MEASure | no |
| REFerence | no |
| STORage | no |
| SYSTem | no |
| TIMebase | YES |
| TRIGger | PARTIAL |
| WAVeform | YES |

- Package management by [Poetry](https://python-poetry.org/).
- Automated processing hooks by [pre-commit](https://pre-commit.com/).
- Code formatting in compliance with [PEP8](https://www.python.org/dev/peps/pep-0008/) by [isort](https://pycqa.github.io/isort/), [black](https://github.com/psf/black), and [flake8](https://gitlab.com/pycqa/flake8).
- Static type checking in compliance with [PEP484](https://www.python.org/dev/peps/pep-0484/) by [mypy](http://www.mypy-lang.org/).
- Test execution with random ordering and code coverage analysis by [pytest](https://docs.pytest.org/en/6.2.x/).
- Automated documentation generation by [sphinx](https://www.sphinx-doc.org/en/master/).

Installing the development environment requires running the following command sequence.

```shell
poetry install
poetry run pre-commit install
```

In order for all tests to pass channel 2 must be connected to the calibration square wave.
