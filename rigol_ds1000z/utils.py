from io import BytesIO
from math import sqrt
from re import search

import matplotlib.image as mpimg  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import numpy as np
from pyvisa import ResourceManager
from pyvisa.errors import VisaIOError


def find_visa():
    # Return the first VISA address which maps to a Rigol DS1000Z.

    RIGOL_IDN_REGEX = "^RIGOL TECHNOLOGIES,DS1[01][057]4Z(-S)?( Plus)?,.+$"

    visa_manager = ResourceManager()

    for visa_name in visa_manager.list_resources():
        try:
            visa_resource = visa_manager.open_resource(visa_name)
            match = search(RIGOL_IDN_REGEX, visa_resource.query("*IDN?"))
            if match:
                return visa_name
        except VisaIOError:
            pass
        finally:
            visa_resource.close()


def process_display(display, show=False, filename=None):
    # If display is True, matplotlib draws a new true to size figure.
    # If filename is provided, image will be saved to file.

    byte_stream = BytesIO(bytearray(display.data))
    with byte_stream:
        img = mpimg.imread(byte_stream, format="jpeg")

        if filename is not None:
            plt.imsave(filename, img)

        if show:
            rigol_xpx, rigol_ypx = 800, 480
            rigol_diagin = 17.8 * 0.393701
            rigol_dpi = sqrt(rigol_xpx ** 2 + rigol_ypx ** 2) / rigol_diagin
            figsize = rigol_xpx / rigol_dpi, rigol_ypx / rigol_dpi

            fig = plt.figure(figsize=figsize, dpi=rigol_dpi)
            ax = fig.add_axes([0, 0, 1, 1])
            ax.axis("off")
            ax.imshow(img)
            plt.show()


def process_waveform(waveform, show=False, filename=None):
    if waveform.format == "ASC":
        ydata = np.array(waveform.data[11:].split(","), dtype=float)
    if waveform.format in ("BYTE", "WORD"):
        ydata = (
            np.array(waveform.data) - waveform.yorigin - waveform.yreference
        ) * waveform.yincrement

    xdata = np.array(range(0, len(ydata)))
    xdata = xdata * waveform.xincrement + waveform.xorigin + waveform.xreference

    if show:
        xlim = (xdata[0], xdata[-1])
        ylim = tuple((np.array([-100, 100]) - waveform.yorigin) * waveform.yincrement)
        plt.plot(xdata, ydata)
        plt.xlim(*xlim)
        plt.xticks(np.linspace(*xlim, 13), rotation=30)
        plt.ylim(*ylim)
        plt.yticks(np.linspace(*ylim, 9))
        plt.ticklabel_format(style="sci", scilimits=(-3, 2))
        plt.grid()
        plt.show()

    if filename is not None:
        np.savetxt(filename, np.transpose(np.vstack((xdata, ydata))), delimiter=",")

    return xdata, ydata
