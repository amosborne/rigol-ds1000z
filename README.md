# rigol-ds1000z

Python library for interfacing with Rigol DS1000Z series oscilloscopes.

This package differs from the alternatives by:
1. Flattening the communication interface with the test equipment so that code can be written in a more compact form.
2. Providing a command line interface for easy display and waveform data capture.

This package strives to maintain the verbiage used in the [Rigol DS1000Z programming manual](https://beyondmeasure.rigoltech.com/acton/attachment/1579/f-0386/1/-/-/-/-/DS1000Z_Programming%20Guide_EN.pdf) as closely as possible. Aside from basic type-casting, command arguments are not validated and instrument responses are not post-processed. Separate utility routines are provided for post-processing display and waveform data.

A function call will send commands associated with the arguments provided and a data structure is always returned with the queried values that belong under that function's domain. Not all interfaces are fully implemented. The basic write, read, and query commands are provided for the user to use in the abscense of a functional interface.

All commands are issued once at a time with a wait after instruction appended. The autoscale and IEEE reset commands enforce a ten and five second sleep respectively to avoid a VISA serial communication timeout or other odd behavior.

Extensive hardware testing has been performed with a Rigol DS1054Z oscilloscope.

Inspired by similar packages iteratively developed by [@jtambasco](https://github.com/jtambasco/RigolOscilloscope), [@jeanyvesb9](https://github.com/jeanyvesb9/Rigol1000z), and [@AlexZettler](https://github.com/AlexZettler/Rigol1000z).

## Usage

This package is available on [PyPI](https://pypi.org/): `pip install rigol-ds1000z`.

The command line interface saves to file a display capture or waveform data from a Rigol DS1000Z series oscilloscope. The first valid VISA address identified is utilized by default.

```shell
rigol-ds1000z --help
rigol-ds1000z --display path/to/file.png
rigol-ds1000z --waveform src path/to/file.csv
```

Example code is shown below and also provided as part of this repository. See the status section for the summary of the implemented functional interfaces or browse the generated documentation [here](https://htmlpreview.github.io/?https://github.com/amosborne/rigol-ds1000z/blob/main/docs/rigol_ds1000z/index.html).

```python
from rigol_ds1000z import Rigol_DS1000Z
from rigol_ds1000z import find_visa, process_display, process_waveform

# find visa address
visa = find_visa()

with Rigol_DS1000Z(visa) as oscope:
    # run and autoscale
    oscope.run()
    oscope.autoscale()

    # reset, self-test, return queried ieee values
    ieee = oscope.ieee(rst=True, tst=True)
    print(ieee.idn)

    # configure channels, return queried channel values
    ch2 = oscope.channel(2, probe=10, coupling="AC", bwlimit=True)
    ch3 = oscope.channel(3, display=True)
    print(ch2.scale, ch3.scale)

    # send SCPI command to clear the display
    oscope.write(":DISP:CLE")

```

## Status

The following SCPI commands are implemented as functional interfaces:
- All base-level commands (ex. `AUT`, `RUN`, `STOP`).
- All IEEE488.2 common commands (ex. `IDN?`, `*RST`, `TST?`).
- All channel commands (ex. `:CHAN1:PROB`).
- All timebase commands (ex. `:TIM:MOD`, `:TIM:DEL:SCAL`).
- All waveform commands (ex. `:WAV:SOUR`, `:WAV:DATA?`).
- The display data query `:DISP:DATA?`.

## Development Notes

- Package management by [Poetry](https://python-poetry.org/).
- Automated processing hooks by [pre-commit](https://pre-commit.com/).
- Code formatting in compliance with [PEP8](https://www.python.org/dev/peps/pep-0008/) by [isort](https://pycqa.github.io/isort/), [black](https://github.com/psf/black), and [flake8](https://gitlab.com/pycqa/flake8).
- Static type checking in compliance with [PEP484](https://www.python.org/dev/peps/pep-0484/) by [mypy](http://www.mypy-lang.org/).
- Test execution with random ordering and code coverage analysis by [pytest](https://docs.pytest.org/en/6.2.x/).
- Automated documentation generation by [pdoc](https://github.com/pdoc3/pdoc).

Installing the development environment requires running the following command sequence.

```shell
poetry install
poetry run pre-commit install
```

In order for all tests to pass, an oscilloscope must be connected and channel 2 must be connected to the calibration square wave.
