#!/usr/bin/env python
#  M Newville <newville@cars.uchicago.edu>
#  The University of Chicago, 2010
#  Epics Open License
#
# Epics Database Records (DBR) Constants and Definitions
#  most of the code here is copied from db_access.h
#

import ctypes
import numpy as np
from enum import IntEnum

from .utils import (PY64_WINDOWS, decode_bytes)

from ctypes import c_short as short_t
from ctypes import c_ushort as ushort_t
from ctypes import c_int as int_t
from ctypes import c_uint as uint_t
from ctypes import c_long as long_t
from ctypes import c_float as float_t
from ctypes import c_double as double_t
from ctypes import c_byte as byte_t
from ctypes import c_ubyte as ubyte_t
from ctypes import c_char as char_t
from ctypes import c_void_p as void_p

if PY64_WINDOWS:
    # Note that Windows needs to be told that chid is 8 bytes for 64-bit,
    # except that Python2 is very weird -- using a 4byte chid for 64-bit, but
    # needing a 1 byte padding!
    from ctypes import c_int64 as chid_t
else:
    from ctypes import c_long as chid_t

MAX_STRING_SIZE = 40
MAX_UNITS_SIZE = 8
MAX_ENUM_STRING_SIZE = 26
MAX_ENUM_STATES = 16

# EPICS2UNIX_EPOCH = 631173600.0 - time.timezone
EPICS2UNIX_EPOCH = 631152000.0

string_t = ctypes.c_char * MAX_STRING_SIZE
# value_offset is set when the CA library connects, indicating the byte offset
# into the response where the first native type element is
value_offset = None


# EPICS Constants
class ECA(IntEnum):
    NORMAL = 1
    TIMEOUT = 80
    IODONE = 339
    ISATTACHED = 424
    BADCHID = 410


class ConnStatus(IntEnum):
    CS_CONN = 2
    OP_CONN_UP = 6
    OP_CONN_DOWN = 7
    CS_NEVER_SEARCH = 4


class ChannelType(IntEnum):
    STRING = 0
    INT = 1
    SHORT = 1
    FLOAT = 2
    ENUM = 3
    CHAR = 4
    LONG = 5
    DOUBLE = 6

    STS_STRING = 7
    STS_SHORT = 8
    STS_INT = 8
    STS_FLOAT = 9
    STS_ENUM = 10
    STS_CHAR = 11
    STS_LONG = 12
    STS_DOUBLE = 13

    TIME_STRING = 14
    TIME_INT = 15
    TIME_SHORT = 15
    TIME_FLOAT = 16
    TIME_ENUM = 17
    TIME_CHAR = 18
    TIME_LONG = 19
    TIME_DOUBLE = 20

    CTRL_STRING = 28
    CTRL_INT = 29
    CTRL_SHORT = 29
    CTRL_FLOAT = 30
    CTRL_ENUM = 31
    CTRL_CHAR = 32
    CTRL_LONG = 33
    CTRL_DOUBLE = 34


class SubscriptionType(IntEnum):
    # create_subscription mask constants
    DBE_VALUE = 1
    DBE_LOG = 2
    DBE_ALARM = 4
    DBE_PROPERTY = 8

ChType = ChannelType


enum_types = (ChType.ENUM, ChType.STS_ENUM, ChType.TIME_ENUM, ChType.CTRL_ENUM)

native_types = (ChType.STRING, ChType.INT, ChType.SHORT, ChType.FLOAT,
                ChType.ENUM, ChType.CHAR, ChType.LONG, ChType.DOUBLE)

status_types = (ChType.STS_STRING, ChType.STS_SHORT, ChType.STS_INT,
                ChType.STS_FLOAT, ChType.STS_ENUM, ChType.STS_CHAR,
                ChType.STS_LONG, ChType.STS_DOUBLE)

time_types = (ChType.TIME_STRING, ChType.TIME_INT, ChType.TIME_SHORT,
              ChType.TIME_FLOAT, ChType.TIME_ENUM, ChType.TIME_CHAR,
              ChType.TIME_LONG, ChType.TIME_DOUBLE)

control_types = (ChType.CTRL_STRING, ChType.CTRL_INT, ChType.CTRL_SHORT,
                 ChType.CTRL_FLOAT, ChType.CTRL_ENUM, ChType.CTRL_CHAR,
                 ChType.CTRL_LONG, ChType.CTRL_DOUBLE)

char_types = (ChType.CHAR, ChType.TIME_CHAR, ChType.CTRL_CHAR)
native_float_types = (ChType.FLOAT, ChType.DOUBLE)


class TimeStamp(ctypes.Structure):
    "emulate epics timestamp"
    _fields_ = [('secs', uint_t),
                ('nsec', uint_t)]

    @property
    def unixtime(self):
        "UNIX timestamp (seconds) from Epics TimeStamp structure"
        return (EPICS2UNIX_EPOCH + self.secs + 1.e-6 * int(1.e-3 * self.nsec))


class TimeType(ctypes.Structure):
    _fields_ = [('status', short_t),
                ('severity', short_t),
                ('stamp', TimeStamp)
                ]

    def to_dict(self):
        return dict(status=self.status,
                    severity=self.severity,
                    timestamp=self.stamp.unixtime,
                    )


class TimeString(TimeType):
    dbr_type = ChannelType.TIME_STRING
    _fields_ = [('value', MAX_STRING_SIZE * char_t)]


class TimeShort(TimeType):
    dbr_type = ChannelType.TIME_SHORT
    _fields_ = [('RISC_pad', short_t),
                ('value', short_t)]


class TimeFloat(TimeType):
    dbr_type = ChannelType.TIME_FLOAT
    _fields_ = [('value', float_t)]


class TimeEnum(TimeType):
    dbr_type = ChannelType.TIME_ENUM
    _fields_ = [('RISC_pad', short_t),
                ('value', ushort_t)]


class TimeChar(TimeType):
    dbr_type = ChannelType.TIME_CHAR
    _fields_ = [('RISC_pad0', short_t),
                ('RISC_pad1', byte_t),
                ('value', byte_t)]


class TimeLong(TimeType):
    dbr_type = ChannelType.TIME_LONG
    _fields_ = [('value', int_t)]


class TimeDouble(TimeType):
    dbr_type = ChannelType.TIME_DOUBLE
    _fields_ = [('RISC_pad', int_t),
                ('value', double_t)]


def _ctrl_lims(type_):
    # DBR types with full control and graphical fields
    field_names = ['upper_disp_limit',
                   'lower_disp_limit',
                   'upper_alarm_limit',
                   'upper_warning_limit',
                   'lower_warning_limit',
                   'lower_alarm_limit',
                   'upper_ctrl_limit',
                   'lower_ctrl_limit',
                   ]

    class ctrl_lims(ctypes.Structure):
        _fields_ = [(field, type_)
                    for field in field_names
                    ]

        ctrl_fields = field_names

        def to_dict(self):
            kwds = super().to_dict()
            kwds.update({attr: getattr(self, attr)
                         for attr in field_names})
            return kwds

    return ctrl_lims


ctrl_lims_short = _ctrl_lims(short_t)
ctrl_lims_byte = _ctrl_lims(byte_t)
ctrl_lims_int = _ctrl_lims(int_t)
ctrl_lims_float = _ctrl_lims(float_t)
ctrl_lims_double = _ctrl_lims(double_t)


class ControlTypeBase(ctypes.Structure):
    _fields_ = [('status', short_t),
                ('severity', short_t),
                ]

    def to_dict(self):
        return dict(severity=self.severity)


class ControlTypeUnits(ControlTypeBase):
    _fields_ = [('units', char_t * MAX_UNITS_SIZE),
                ]

    def to_dict(self):
        kwds = super().to_dict()
        kwds['units'] = decode_bytes(self.units)
        return kwds


class ControlTypePrecision(ControlTypeBase):
    _fields_ = [('precision', short_t),
                ('RISC_pad', short_t),
                ('units', char_t * MAX_UNITS_SIZE),
                ]

    def to_dict(self):
        kwds = super().to_dict()
        kwds['precision'] = self.precision
        kwds['units'] = decode_bytes(self.units)
        return kwds


class ctrl_enum(ControlTypeBase):
    dbr_type = ChannelType.CTRL_ENUM

    _fields_ = [('no_str', short_t),
                ('strs', (char_t * MAX_ENUM_STRING_SIZE) * MAX_ENUM_STATES),
                ('value', ushort_t)
                ]

    def to_dict(self):
        kwds = super().to_dict()
        if self.no_str > 0:
            kwds['enum_strs'] = tuple(decode_bytes(self.strs[i].value)
                                      for i in range(self.no_str))

        return kwds


class ctrl_short(ctrl_lims_short, ControlTypeUnits):
    dbr_type = ChannelType.CTRL_SHORT
    _fields_ = [('value', short_t)]


class ctrl_char(ctrl_lims_byte, ControlTypeUnits):
    dbr_type = ChannelType.CTRL_CHAR
    _fields_ = [('RISC_pad', byte_t),
                ('value', ubyte_t)
                ]


class ctrl_long(ctrl_lims_int, ControlTypeUnits):
    dbr_type = ChannelType.CTRL_LONG
    _fields_ = [('value', int_t)]


class ctrl_float(ctrl_lims_float, ControlTypePrecision):
    dbr_type = ChannelType.CTRL_FLOAT
    _fields_ = [('value', float_t)]


class ctrl_double(ctrl_lims_double, ControlTypePrecision):
    dbr_type = ChannelType.CTRL_DOUBLE
    _fields_ = [('value', double_t)]


class event_handler_args(ctypes.Structure):
    '''event handler arguments'''
    _fields_ = [('usr', ctypes.py_object),
                ('chid', chid_t),
                ('type', long_t),
                ('count', long_t),
                ('raw_dbr', void_p),
                ('status', int_t)]


class connection_args(ctypes.Structure):
    '''connection arguments'''
    _fields_ = [('chid', chid_t),
                ('op', long_t)]


_numpy_map = {
    ChType.INT: np.int16,
    ChType.FLOAT: np.float32,
    ChType.ENUM: np.uint16,
    ChType.CHAR: np.uint8,
    ChType.LONG: np.int32,
    ChType.DOUBLE: np.float64
}


# map of Epics DBR types to ctypes types
_ftype_to_ctype = {
    ChType.STRING: string_t,
    ChType.INT: short_t,
    ChType.FLOAT: float_t,
    ChType.ENUM: ushort_t,
    ChType.CHAR: ubyte_t,
    ChType.LONG: int_t,
    ChType.DOUBLE: double_t,

    ChType.STS_STRING: string_t,
    ChType.STS_INT: short_t,
    ChType.STS_FLOAT: float_t,
    ChType.STS_ENUM: ushort_t,
    ChType.STS_CHAR: ubyte_t,
    ChType.STS_LONG: int_t,
    ChType.STS_DOUBLE: double_t,

    ChType.TIME_STRING: TimeString,
    ChType.TIME_INT: TimeShort,
    ChType.TIME_SHORT: TimeShort,
    ChType.TIME_FLOAT: TimeFloat,
    ChType.TIME_ENUM: TimeEnum,
    ChType.TIME_CHAR: TimeChar,
    ChType.TIME_LONG: TimeLong,
    ChType.TIME_DOUBLE: TimeDouble,

    # Note: there is no ctrl string in the C definition
    ChType.CTRL_STRING: TimeString,
    ChType.CTRL_SHORT: ctrl_short,
    ChType.CTRL_INT: ctrl_short,
    ChType.CTRL_FLOAT: ctrl_float,
    ChType.CTRL_ENUM: ctrl_enum,
    ChType.CTRL_CHAR: ctrl_char,
    ChType.CTRL_LONG: ctrl_long,
    ChType.CTRL_DOUBLE: ctrl_double
}


_native_map = {
    ChType.STRING: ChType.STRING,
    ChType.INT: ChType.INT,
    ChType.FLOAT: ChType.FLOAT,
    ChType.ENUM: ChType.ENUM,
    ChType.CHAR: ChType.CHAR,
    ChType.LONG: ChType.LONG,
    ChType.DOUBLE: ChType.DOUBLE,

    ChType.STS_STRING: ChType.STRING,
    ChType.STS_INT: ChType.INT,
    ChType.STS_FLOAT: ChType.FLOAT,
    ChType.STS_ENUM: ChType.ENUM,
    ChType.STS_CHAR: ChType.CHAR,
    ChType.STS_LONG: ChType.LONG,
    ChType.STS_DOUBLE: ChType.DOUBLE,

    ChType.TIME_STRING: ChType.STRING,
    ChType.TIME_INT: ChType.INT,
    ChType.TIME_SHORT: ChType.SHORT,
    ChType.TIME_FLOAT: ChType.FLOAT,
    ChType.TIME_ENUM: ChType.ENUM,
    ChType.TIME_CHAR: ChType.CHAR,
    ChType.TIME_LONG: ChType.LONG,
    ChType.TIME_DOUBLE: ChType.DOUBLE,

    ChType.CTRL_STRING: ChType.STRING,
    ChType.CTRL_SHORT: ChType.SHORT,
    ChType.CTRL_INT: ChType.INT,
    ChType.CTRL_FLOAT: ChType.FLOAT,
    ChType.CTRL_ENUM: ChType.ENUM,
    ChType.CTRL_CHAR: ChType.CHAR,
    ChType.CTRL_LONG: ChType.LONG,
    ChType.CTRL_DOUBLE: ChType.DOUBLE,
}


def native_type(ftype):
    '''return native field type from TIME or CTRL variant'''
    global _native_map
    return _native_map[ftype]


def promote_type(ftype, use_time=False, use_ctrl=False):
    """Promotes a native field type to its TIME or CTRL variant.

    Returns
    -------
    ftype : int
        the promoted field value.
    """
    ftype = ChType(_native_map.get(ftype, None))

    if use_ctrl:
        ftype += ChType.CTRL_STRING
    elif use_time:
        ftype += ChType.TIME_STRING

    if ftype == ChType.CTRL_STRING:
        return ChType.TIME_STRING
    return ftype
