"""Smoke tests for the installed public API."""

from zend import VERSION, AsyncZend, Zend, __version__


def test_public_client_surface_imports() -> None:
    assert Zend.__name__ == "Zend"
    assert AsyncZend.__name__ == "AsyncZend"
    assert VERSION == __version__ == "0.1.0"
