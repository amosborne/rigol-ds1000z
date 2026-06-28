from random import randint

from pytest import fixture

from rigol_ds1000z import Rigol_DS1000Z


@fixture(scope="session")
def connection():
    """Open the VISA connection once for the whole test session."""
    with Rigol_DS1000Z() as oscope:
        yield oscope


@fixture
def oscope(connection):
    """Reset the instrument to a known state before each test."""
    connection.rst()
    return connection


@fixture
def n():
    """A random channel number (1 through 4) for channel-agnostic tests."""
    return randint(1, 4)
