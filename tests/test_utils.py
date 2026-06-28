import os

import rigol_ds1000z.utils as utils
from rigol_ds1000z import Rigol_DS1000Z, process_display, process_waveform


class _FakeResource:
    def __init__(self, idn):
        self._idn = idn

    def query(self, _cmd):
        return self._idn

    def close(self):
        pass


class _FakeManager:
    def __init__(self, resources):
        self._resources = resources

    def list_resources(self):
        return tuple(self._resources)

    def open_resource(self, name):
        return self._resources[name]


def test_find_visas_skips_unavailable_backend(monkeypatch):
    # No NI-VISA installed makes ResourceManager("@ivi") raise a plain OSError;
    # find_visas should skip that backend and still discover via "@py" instead
    # of letting the error propagate.
    rigol_idn = "RIGOL TECHNOLOGIES,DS1104Z,DS1ZA00000000,00.04.05"
    resource = "TCPIP::192.168.0.2::INSTR"

    def fake_resource_manager(backend):
        if backend == "@ivi":
            raise OSError("Could not open VISA library")
        return _FakeManager({resource: _FakeResource(rigol_idn)})

    monkeypatch.setattr(utils, "ResourceManager", fake_resource_manager)

    assert utils.find_visas() == [(resource, "@py")]


def test_process_display():
    with Rigol_DS1000Z() as oscope:
        oscope.autoscale()
        filename = "tests/test_process_display_data.png"
        process_display(oscope.display(), filename=filename)
        assert os.path.isfile(filename)
        os.remove(filename)


def test_process_waveform():
    with Rigol_DS1000Z() as oscope:
        oscope.autoscale()
        filename = "tests/test_process_waveform.csv"
        process_waveform(oscope.waveform(source=2), filename=filename)
        assert os.path.isfile(filename)
        os.remove(filename)
