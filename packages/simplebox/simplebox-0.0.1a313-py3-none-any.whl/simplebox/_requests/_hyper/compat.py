# -*- coding: utf-8 -*-
# flake8: noqa
"""
_hyper/compat
~~~~~~~~~~~~

Normalizes the Python 2/3 API for internal use.
"""
from contextlib import contextmanager
import sys
import zlib

try:
    from . import ssl_compat
except ImportError:
    # TODO log?
    ssl_compat = None

_ver = sys.version_info
is_py2 = _ver[0] == 2
is_py2_7_9_or_later = _ver[0] >= 2 and _ver[1] >= 7 and _ver[2] >= 9
is_py3 = _ver[0] == 3
is_py3_3 = is_py3 and _ver[1] == 3


@contextmanager
def ignore_missing():
    try:
        yield
    except (AttributeError, NotImplementedError):  # pragma: no cover
        pass


from urllib.parse import urlencode, urlparse, urlsplit

imap = map


def to_byte(char):
    return char


def decode_hex(b):
    return bytes.fromhex(b)


def write_to_stdout(data):
    sys.stdout.buffer.write(data + b'\n')
    sys.stdout.buffer.flush()


zlib_compressobj = zlib.compressobj

if is_py3_3:
    ssl = ssl_compat
else:
    import ssl

unicode = str
bytes = bytes
