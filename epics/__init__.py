from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

__doc__ = """
   epics channel access python module

   version: %s
   Principal Authors:
      Matthew Newville <newville@cars.uchicago.edu> CARS, University of Chicago
      Angus Gratton <angus.gratton@anu.edu.au>, Australian National University

== License:

   Except where explicitly noted, this file and all files in this
   distribution are licensed under the Epics Open License See license.txt in
   the top-level directory of this distribution.

== Overview:
   Python Interface to the Epics Channel Access
   protocol of the Epics control system.

""" % (__version__)


import time
import sys
from . import ca
from . import dbr
from . import context
from . import pv
from . import alarm
from . import multiproc

from .pv import PV
from .alarm import (Alarm, )
from .multiproc import (CAProcess, CAPool)
from .alarm import (NO_ALARM, MINOR_ALARM, MAJOR_ALARM, INVALID_ALARM)

from .coroutines import (caget, caput, get_ctrlvars, get_timevars,
                         get_timestamp, get_severity, get_precision,
                         get_enum_strings, cainfo, caget_many)
