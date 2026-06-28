"""Declarative description of the uniform SCPI subsystem pattern.

Across every subsystem each parameter repeats one idea: if a value was given,
write ``<command> <value>``; then read it back with ``<command>?`` and parse the
response. A ``Field`` subclass captures that for one value type -- how to
``format`` a set value and ``parse`` a queried one -- and ``write_fields`` /
``read_fields`` drive a list of them. Irregular cases (write ordering, mode
dispatch, binary transfers) stay as explicit code in the subsystem.
"""


class Field:
    """A SCPI parameter; subclasses define ``format`` (set) and ``parse`` (read).

    ``command`` may contain a ``{n}`` placeholder filled from the call context.
    Values listed in ``keywords`` (e.g. ``AUTO``, ``MIN``) pass through verbatim
    in both directions instead of being formatted/parsed.
    """

    def __init__(self, name, command, keywords=()):
        self.name = name
        self.command = command
        self.keywords = keywords

    def format(self, value):
        raise NotImplementedError

    def parse(self, response):
        raise NotImplementedError

    def set(self, oscope, value, **ctx):
        token = value if value in self.keywords else self.format(value)
        oscope.write(self.command.format(**ctx) + " " + token)

    def get(self, oscope, **ctx):
        response = oscope.query(self.command.format(**ctx) + "?")
        return response if response in self.keywords else self.parse(response)


class Float(Field):
    """A float, sent in 6-digit scientific notation (matching the scope's reports)."""

    def format(self, value):
        return "{:.6e}".format(value)

    def parse(self, response):
        return float(response)


class Int(Field):
    def format(self, value):
        return "{:d}".format(value)

    def parse(self, response):
        return int(response)


class String(Field):
    def format(self, value):
        return str(value)

    def parse(self, response):
        return response


class Bool(Field):
    """A boolean written/read as a pair of tokens (default ``1``/``0``).

    Parameters that use named tokens pass their own, e.g.
    ``Bool("bwlimit", ":CHAN{n}:BWL", true="20M", false="OFF")``.
    """

    def __init__(self, name, command, true="1", false="0"):
        super().__init__(name, command)
        self.true = true
        self.false = false

    def format(self, value):
        return self.true if value else self.false

    def parse(self, response):
        return response == self.true


def write_fields(oscope, fields, values, **ctx):
    """Write each provided (non-``None``) value, in field-declaration order."""
    for field in fields:
        value = values.get(field.name)
        if value is not None:
            field.set(oscope, value, **ctx)


def read_fields(oscope, fields, **ctx):
    """Query every field; return ``{name: parsed value}``."""
    return {field.name: field.get(oscope, **ctx) for field in fields}
