#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import time

from . import toExternalObject

IGNORE_RESULT = object()

class RunnerResult(object):

    def __init__(self, group_name, runner_num, run_time, elapsed, iteration,
                 result=None, exception=None, epoch=None, custom_timers={}):
        self.result = result
        self.elapsed = elapsed
        self.run_time = run_time
        self.exception = exception
        self.iteration = iteration
        self.runner_num = runner_num
        self.group_name = group_name
        self.custom_timers = custom_timers or {}
        self.epoch = epoch or time.mktime(time.localtime())

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "(%s, %s, %s, %s)" % (self.group_name, self.runner_num,
									 self.iteration, self.run_time)

    @property
    def error(self):
        return str(self.exception) if self.exception else ''

    @property
    def output(self):
        return repr(self.result) if self.result else ''

    @property
    def timers(self):
        return self.custom_timers

    def timers_to_string(self, delim='\t'):
        lst = ['%s:%f' % (k, v) for k, v in self.custom_timers.iteritems()]
        return delim.join(lst)

    def toExternalObject(self):
        external = {}
        external['epoch'] = self.epoch
        external['result'] = self.result
        external['elapsed'] = self.elapsed
        external['run_time'] = self.run_time
        external['exception'] = self.exception
        external['iteration'] = self.iteration
        external['runner_num'] = self.runner_num
        external['group_name'] = self.group_name
        external['custom_timers'] = toExternalObject(self.custom_timers)
        return external
