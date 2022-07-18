from collections import namedtuple

DISPLAY = namedtuple("DISPLAY", "data")


def display(oscope):
    return DISPLAY(data=oscope.visa_rsrc.query_binary_values(":DISP:DATA?", "B"))
