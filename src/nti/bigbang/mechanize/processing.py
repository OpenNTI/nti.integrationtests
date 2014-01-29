#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import sys
import time
import inspect
import threading
import traceback
import multiprocessing
from cStringIO import StringIO

from zope import interface
from zope.event import notify

from .context import Context
from . import toExternalObject
from .result import RunnerResult
from .result import IGNORE_RESULT
from .context import TimerResultMixin
from . import interfaces as mc_interfaces

def validate_context(context):
	assert isinstance(context, Context), 'must specify a valid context'

	assert 	hasattr(context, 'run_time') or  hasattr(context, 'max_iterations'), \
			"must specify a valid max number of iterations or runtime in secs"

	if context.run_time is not None:
		assert context.run_time > 0, "must specify a valid run time in secs"

	if context.max_iterations is not None:
		assert context.max_iterations > 0, "must specify a valid max number of iterations"

	assert context.runners > 0, "must specify a valid number of runners"

	assert 	inspect.isfunction(context.target) or callable(context.target), \
			"must specify a valid target"

	if context.target_args:
		assert tuple(context.target_args), "must specify a valid target arguments"

	assert context.group_name, "must specify a valid runner group name"
	return context

@interface.implementer(mc_interfaces.ICallable)
def noop(*args, **kwargs):
	pass

class RunnerGroup(multiprocessing.Process):

	queue = None
	_results = ()

	def __init__(self, context, validate=True, queue=None, *args, **kwargs):
		super(RunnerGroup, self).__init__(*args, **kwargs)
		self.context = validate_context(context) if validate else context
		if queue:
			self.queue = queue
		if self.hold_results:
			self._results = []

	def __str__(self):
		return self.group_name

	def __repr__(self):
		return "(%s, %s, %s, %s)" % (self.group_name, self.runners, self.run_time,
									 self.max_iterations)

	# ----------------

	def _add_result(self, runner):
		if self.hold_results:
			self._results.extend(runner.results)

	@property
	def results(self):
		return self._results

	@property
	def runners(self):
		return self.context.runners

	@property
	def group_name(self):
		return self.context.group_name

	@property
	def run_time(self):
		return getattr(self.context, 'run_time', None)

	@property
	def max_iterations(self):
		return getattr(self.context, 'max_iterations', None)

	@property
	def rampup(self):
		return getattr(self.context, 'rampup', 0)

	@property
	def use_threads(self):
		return getattr(self.context, 'use_threads', False)

	@property
	def hold_results(self):
		return getattr(self.context, 'hold_results', False)

	@property
	def target(self):
		return self.context.target

	@property
	def target_args(self):
		return self.context.target_args

	@property
	def setup(self):
		return self.context.setup

	@property
	def teardown(self):
		return self.context.teardown

	def run(self):
		callables = []

		self.setup(self.context)
		logger.info("group '%s' started", self.group_name)

		t = time.time()
		try:
			for i in xrange(self.runners):
				spacing = float(self.rampup) / float(self.runners)
				if i > 0 and spacing:
					time.sleep(spacing)

				target = TargetRunner(runner_num=i + 1, context=self.context,
									  queue=self.queue)
				if self.use_threads:
					runner = threading.Thread(target=target, args=())
				else:
					runner = multiprocessing.Process(target=target, args=())

				callables.append((runner, target))
				runner.start()

			for runner, target in callables:
				runner.join()
				self._add_result(target)
		finally:
			self.teardown(self.context)
			elapsed = time.time() - t
			logger.info("group '%s' completed in (%.3f)s", self.group_name, elapsed)

class TargetRunner(object):

	_results = ()

	def __init__(self, runner_num, context, queue=None):
		self.queue = queue
		self.context = context
		self.runner_num = runner_num
		if self.hold_results:
			self._results = []

	def __str__(self):
		return "(%s, %s)" % (self.group_name, self.runner_num)

	def __repr__(self):
		return self.__str__()

	def __call__(self, *args, **kwargs):
		self.run()

	# ----------------

	@property
	def results(self):
		return self._results

	@property
	def hold_results(self):
		return getattr(self.context, 'hold_results', False)

	@property
	def run_time(self):
		return getattr(self.context, 'run_time', None)

	@property
	def max_iterations(self):
		return getattr(self.context, 'max_iterations', None)

	@property
	def call_wait_time(self):
		return getattr(self.context, 'call_wait_time', None)

	@property
	def start_time(self):
		return getattr(self.context, 'start_time', time.time())

	@property
	def target(self):
		return self.context.target

	@property
	def target_args(self):
		return self.context.target_args

	@property
	def group_name(self):
		return self.context.group_name

	@property
	def allow_context(self):
		spec = inspect.getargspec(self.target)
		return (spec.args and spec.args[-1] == '__context__') or spec.keywords

	@property
	def allow_keywords(self):
		spec = inspect.getargspec(self.target)
		return True if spec.keywords else False

	def run(self):
		elapsed = 0
		iterations = 0
		start_time = self.start_time

		logger.info("runner '%s' started. Run time=%s, Max iterations=%s",
					self.runner_num, self.run_time, self.max_iterations)

		can_bind_context = self.allow_context
		can_bind_any_keyword = self.allow_keywords

		while	(self.run_time and elapsed < self.run_time) or \
				(self.max_iterations and iterations < self.max_iterations):

			result = None
			exception = None
			start = time.time()
			try:
				if can_bind_any_keyword:
					result = self.target(*self.target_args,
										 __context__=self.context,
										 __runner__=self.runner_num,
										 __iteration__=iterations)
				elif can_bind_context:
					result = self.target(*self.target_args, __context__=self.context)
				else:
					result = self.target(*self.target_args)
			except Exception:
				sio = StringIO()
				exc_type, exc_value, exc_traceback = sys.exc_info()
				traceback.print_exception(exc_type, exc_value, exc_traceback, file=sio)
				sio.seek(0)
				exception = sio.read()

			iterations = iterations + 1
			run_time = time.time() - start

			if self.call_wait_time:
				time.sleep(self.call_wait_time)

			elapsed = time.time() - start_time

			if IGNORE_RESULT != result:

				if isinstance(result, TimerResultMixin):
					custom_timers = result.timers
					result = result.result
				else:
					custom_timers = None

				result = toExternalObject(result) if result is not None else result
				runner_result = RunnerResult(group_name=self.group_name,
											 runner_num=self.runner_num,
											 run_time=run_time,
											 elapsed=elapsed,
											 iteration=iterations,
											 result=result,
											 exception=exception,
											 custom_timers=custom_timers)

				if self.queue:
					self.queue.put(runner_result)
				else:
					notify(runner_result)

				if self.hold_results:
					self._results.append(runner_result)

		logger.info("runner '%s' completed. Time=%s, iterations=%s", self.runner_num,
					elapsed, iterations)
