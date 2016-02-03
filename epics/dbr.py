#!/usr/bin/env python
#  M Newville <newville@cars.uchicago.edu>
#  The University of Chicago, 2010
#  Epics Open License
#
# Epics Database Records (DBR) Constants and Definitions
#  most of the code here is copied from db_access.h
#
""" constants and declaration of data types for Epics database records
This is mostly copied from CA header files
"""
import ctypes
import numpy as np

from .utils import PY64_WINDOWS

# EPICS Constants
ECA_NORMAL = 1
ECA_TIMEOUT = 80
ECA_IODONE = 339
ECA_ISATTACHED = 424
ECA_BADCHID = 410

CS_CONN = 2
OP_CONN_UP = 6
OP_CONN_DOWN = 7

CS_NEVER_SEARCH = 4
#
# Note that DBR_XXX should be replaced with dbr.XXX
#
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

MAX_STRING_SIZE = 40
MAX_UNITS_SIZE = 8
MAX_ENUM_STRING_SIZE = 26
MAX_ENUMS = 16

# EPICS2UNIX_EPOCH = 631173600.0 - time.timezone
EPICS2UNIX_EPOCH = 631152000.0

# create_subscription mask constants
DBE_VALUE = 1
DBE_LOG = 2
DBE_ALARM = 4
DBE_PROPERTY = 8

chid_t = ctypes.c_long

# Note that Windows needs to be told that chid is 8 bytes for 64-bit, except
# that Python2 is very weird -- using a 4byte chid for 64-bit, but needing a 1
# byte padding!
if PY64_WINDOWS:
    chid_t = ctypes.c_int64

short_t = ctypes.c_short
ushort_t = ctypes.c_ushort
int_t = ctypes.c_int
uint_t = ctypes.c_uint
long_t = ctypes.c_long
ulong_t = ctypes.c_ulong
float_t = ctypes.c_float
double_t = ctypes.c_double
byte_t = ctypes.c_byte
ubyte_t = ctypes.c_ubyte
string_t = ctypes.c_char * MAX_STRING_SIZE
char_t = ctypes.c_char
char_p = ctypes.c_char_p
void_p = ctypes.c_void_p
py_obj = ctypes.py_object

value_offset = None


# extended DBR types:
class TimeStamp(ctypes.Structure):
    "emulate epics timestamp"
    _fields_ = [('secs', uint_t),
                ('nsec', uint_t)]


class _stat_sev(ctypes.Structure):
    _fields_ = [('status', short_t),
                ('severity', short_t),
                ]


class _stat_sev_units(_stat_sev):
    _fields_ = [('units', char_t * MAX_UNITS_SIZE),
                ]


class _stat_sev_ts(ctypes.Structure):
    _fields_ = [('status', short_t),
                ('severity', short_t),
                ('stamp', TimeStamp)
                ]


def make_unixtime(stamp):
    "UNIX timestamp (seconds) from Epics TimeStamp structure"
    return (EPICS2UNIX_EPOCH + stamp.secs + 1.e-6 * int(1.e-3 * stamp.nsec))


class time_string(_stat_sev_ts):
    "dbr time string"
    _fields_ = [('value', MAX_STRING_SIZE * char_t)]


class time_short(_stat_sev_ts):
    "dbr time short"
    _fields_ = [('RISC_pad', short_t),
                ('value', short_t)]


class time_float(_stat_sev_ts):
    "dbr time float"
    _fields_ = [('value', float_t)]


class time_enum(_stat_sev_ts):
    "dbr time enum"
    _fields_ = [('RISC_pad', short_t),
                ('value', ushort_t)]


class time_char(_stat_sev_ts):
    "dbr time char"
    _fields_ = [('RISC_pad0', short_t),
                ('RISC_pad1', byte_t),
                ('value', byte_t)]


class time_long(_stat_sev_ts):
    "dbr time long"
    _fields_ = [('value', int_t)]


class time_double(_stat_sev_ts):
    "dbr time double"
    _fields_ = [('RISC_pad', int_t),
                ('value', double_t)]


def _ctrl_lims(t):
    # DBR types with full control and graphical fields
    # yes, this strange order is as in db_access.h!!!

    class ctrl_lims(ctypes.Structure):
        _fields_ = [('upper_disp_limit', t),
                    ('lower_disp_limit', t),
                    ('upper_alarm_limit', t),
                    ('upper_warning_limit', t),
                    ('lower_warning_limit', t),
                    ('lower_alarm_limit', t),
                    ('upper_ctrl_limit', t),
                    ('lower_ctrl_limit', t),
                    ]

    return ctrl_lims


class ctrl_enum(_stat_sev):
    "dbr ctrl enum"
    _fields_ = [('no_str', short_t),
                ('strs', (char_t * MAX_ENUM_STRING_SIZE) * MAX_ENUMS),
                ('value', ushort_t)
                ]


class ctrl_short(_ctrl_lims(short_t), _stat_sev_units):
    "dbr ctrl short"
    _fields_ = [('value', short_t)]


class ctrl_char(_ctrl_lims(byte_t), _stat_sev_units):
    "dbr ctrl long"
    _fields_ = [('RISC_pad', byte_t),
                ('value', ubyte_t)
                ]


class ctrl_long(_ctrl_lims(int_t), _stat_sev_units):
    "dbr ctrl long"
    _fields_ = [('value', int_t)]


class _ctrl_units(_stat_sev):
    _fields_ = [('precision', short_t),
                ('RISC_pad', short_t),
                ('units', char_t * MAX_UNITS_SIZE),
                ]


class ctrl_float(_ctrl_lims(float_t), _ctrl_units):
    "dbr ctrl float"
    _fields_ = [('value', float_t)]


class ctrl_double(_ctrl_lims(double_t), _ctrl_units):
    "dbr ctrl double"
    _fields_ = [('value', double_t)]


NP_Map = {INT: np.int16,
          FLOAT: np.float32,
          ENUM: np.uint16,
          CHAR: np.uint8,
          LONG: np.int32,
          DOUBLE: np.float64}


# map of Epics DBR types to ctypes types
Map = {STRING: string_t,
       INT: short_t,
       FLOAT: float_t,
       ENUM: ushort_t,
       CHAR: ubyte_t,
       LONG: int_t,
       DOUBLE: double_t,

       # TODO: these right?
       STS_STRING: string_t,
       STS_INT: short_t,
       STS_FLOAT: float_t,
       STS_ENUM: ushort_t,
       STS_CHAR: ubyte_t,
       STS_LONG: int_t,
       STS_DOUBLE: double_t,

       TIME_STRING: time_string,
       TIME_INT: time_short,
       TIME_SHORT: time_short,
       TIME_FLOAT: time_float,
       TIME_ENUM: time_enum,
       TIME_CHAR: time_char,
       TIME_LONG: time_long,
       TIME_DOUBLE: time_double,
       # Note: there is no ctrl string in the C definition
       CTRL_STRING: time_string,
       CTRL_SHORT: ctrl_short,
       CTRL_INT: ctrl_short,
       CTRL_FLOAT: ctrl_float,
       CTRL_ENUM: ctrl_enum,
       CTRL_CHAR: ctrl_char,
       CTRL_LONG: ctrl_long,
       CTRL_DOUBLE: ctrl_double
       }


NativeMap = {
    STRING: STRING,
    INT: INT,
    FLOAT: FLOAT,
    ENUM: ENUM,
    CHAR: CHAR,
    LONG: LONG,
    DOUBLE: DOUBLE,

    STS_STRING: STRING,
    STS_INT: INT,
    STS_FLOAT: FLOAT,
    STS_ENUM: ENUM,
    STS_CHAR: CHAR,
    STS_LONG: LONG,
    STS_DOUBLE: DOUBLE,

    TIME_STRING: STRING,
    TIME_INT: INT,
    TIME_SHORT: SHORT,
    TIME_FLOAT: FLOAT,
    TIME_ENUM: ENUM,
    TIME_CHAR: CHAR,
    TIME_LONG: LONG,
    TIME_DOUBLE: DOUBLE,

    # Note: there is no ctrl string in the C definition
    CTRL_STRING: TIME_STRING,  # <-- correct
    CTRL_SHORT: SHORT,
    CTRL_INT: INT,
    CTRL_FLOAT: FLOAT,
    CTRL_ENUM: ENUM,
    CTRL_CHAR: CHAR,
    CTRL_LONG: LONG,
    CTRL_DOUBLE: DOUBLE,
}


def native_type(ftype):
    "return native field type from TIME or CTRL variant"
    return NativeMap[ftype]


def promote_type(ftype, use_time=False, use_ctrl=False):
    """Promotes a native field type to its TIME or CTRL variant.

    Returns
    -------
    ftype : int
        the promoted field value.
    """
    if use_ctrl:
        ftype += CTRL_STRING
    elif use_time:
        ftype += TIME_STRING
    if ftype == CTRL_STRING:
        ftype = TIME_STRING
    return ftype


def Name(ftype, reverse=False):
    """ convert integer data type to dbr Name, or optionally reverse that
    look up (that is, name to integer)"""
    m = {STRING: 'STRING',
         INT: 'INT',
         FLOAT: 'FLOAT',
         ENUM: 'ENUM',
         CHAR: 'CHAR',
         LONG: 'LONG',
         DOUBLE: 'DOUBLE',

         STS_STRING: 'STS_STRING',
         STS_SHORT: 'STS_SHORT',
         STS_INT: 'STS_INT',
         STS_FLOAT: 'STS_FLOAT',
         STS_ENUM: 'STS_ENUM',
         STS_CHAR: 'STS_CHAR',
         STS_LONG: 'STS_LONG',
         STS_DOUBLE: 'STS_DOUBLE',

         TIME_STRING: 'TIME_STRING',
         TIME_SHORT: 'TIME_SHORT',
         TIME_FLOAT: 'TIME_FLOAT',
         TIME_ENUM: 'TIME_ENUM',
         TIME_CHAR: 'TIME_CHAR',
         TIME_LONG: 'TIME_LONG',
         TIME_DOUBLE: 'TIME_DOUBLE',

         CTRL_STRING: 'CTRL_STRING',
         CTRL_SHORT: 'CTRL_SHORT',
         CTRL_FLOAT: 'CTRL_FLOAT',
         CTRL_ENUM: 'CTRL_ENUM',
         CTRL_CHAR: 'CTRL_CHAR',
         CTRL_LONG: 'CTRL_LONG',
         CTRL_DOUBLE: 'CTRL_DOUBLE',
         }
    if reverse:
        name = ftype.upper()
        if name in list(m.values()):
            for key, val in m.items():
                if name == val:
                    return key
    return m.get(ftype, 'unknown')


def cast_args(args):
    """returns casted array contents

    returns: [dbr_ctrl or dbr_time struct,
              count * native_type structs]

    If data is already of a native_type, the first
    value in the list will be None.
    """
    ftype = args.type
    ntype = native_type(ftype)
    if ftype != ntype:
        native_start = args.raw_dbr + value_offset[ftype]
        return [ctypes.cast(args.raw_dbr,
                            ctypes.POINTER(Map[ftype])).contents,
                ctypes.cast(native_start,
                            ctypes.POINTER(args.count * Map[ntype])).contents
                ]
    else:
        return [None,
                ctypes.cast(args.raw_dbr,
                            ctypes.POINTER(args.count * Map[ftype])).contents
                ]


class event_handler_args(ctypes.Structure):
    "event handler arguments"
    _fields_ = [('usr', ctypes.py_object),
                ('chid', chid_t),
                ('type', long_t),
                ('count', long_t),
                ('raw_dbr', void_p),
                ('status', int_t)]

class connection_args(ctypes.Structure):
    "connection arguments"
    _fields_ = [('chid', chid_t),
                ('op', long_t)]
