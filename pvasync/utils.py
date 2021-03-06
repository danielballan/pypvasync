import os
import time
from platform import architecture

PY64_WINDOWS = (os.name == 'nt' and architecture()[0].startswith('64'))


def format_time(tstamp):
    """simple formatter for time values"""
    tstamp, frac = divmod(tstamp, 1)
    tstamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(tstamp))
    frac = round(1.e5 * frac)
    return "%s.%5.5i" % (tstamp, frac)


def decode_bytes(bytes_, encoding='latin-1'):
    try:
        bytes_ = bytes_[:bytes_.index(0)]
    except ValueError:
        pass

    return bytes_.decode(encoding)
