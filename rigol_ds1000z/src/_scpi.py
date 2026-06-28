"""Declarative description of the uniform SCPI subsystem pattern.

Across every subsystem each parameter repeats one idea: if a value was given,
write ``<command> <value>``; then read it back with ``<command>?`` and parse the
response. A ``Field`` is that description as data -- the SCPI command plus how to
format a set value and parse a queried one -- and ``write_fields``/``read_fields``
drive a list of them. Irregular cases (write ordering, mode dispatch, binary
transfers) stay as explicit code in the subsystem.
"""

from collections import namedtuple

# ``command`` may contain a ``{n}`` placeholder filled from call context (channels).
Field = namedtuple("Field", "name command fmt parse")


def source_token(source):
    """Format a channel source as ``CHAN<n>`` (int) or a literal (str)."""
    return source if isinstance(source, str) else "CHAN{:d}".format(source)


def source_value(response):
    """Coerce a queried source into an int channel number or a literal string."""
    return int(response[-1]) if response.startswith("CHAN") else response


# Typed fields pair a value formatter with a response parser. Floats use 6-digit
# scientific notation to match how the DS1000Z reports them (e.g. 2.000000e+00).
def Float(name, command):
    return Field(name, command, "{:.6e}".format, float)


def Int(name, command):
    return Field(name, command, "{:d}".format, int)


def Bool(name, command, true="1", false="0"):
    """A boolean, written and read back as a pair of tokens (default ``1``/``0``).

    Parameters that use named tokens pass their own, e.g.
    ``Bool("bwlimit", ":CHAN{n}:BWL", true="20M", false="OFF")``.
    """
    return Field(name, command, lambda v: true if v else false, lambda r: r == true)


def String(name, command):
    return Field(name, command, str, str)


def Source(name, command):
    return Field(name, command, source_token, source_value)


def write_fields(oscope, fields, values, **ctx):
    """Write each provided (non-``None``) value, in field-declaration order."""
    for field in fields:
        value = values.get(field.name)
        if value is not None:
            oscope.write(field.command.format(**ctx) + " " + field.fmt(value))


def read_fields(oscope, fields, **ctx):
    """Query every field; return ``{name: parsed value}``."""
    return {
        field.name: field.parse(oscope.query(field.command.format(**ctx) + "?"))
        for field in fields
    }
