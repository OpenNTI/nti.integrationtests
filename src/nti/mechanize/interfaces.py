#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
Store interfaces

$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

from zope import schema
from zope import interface

class ICallable(interface.Interface):

	def __call__(*args, **kwargs):
		pass

class IExternalizable(interface.Interface):

	def toExternalObject():
		pass

class IContext(IExternalizable):
	test_name = schema.TextLine(title="test name", required=True)
	serialize = schema.Bool(title="serialize option", required=False, default=False)
	base_path = schema.TextLine(title="base path directory", required=False)
	output_dir = schema.TextLine(title="output path directory", required=False)
	script_setup = schema.Object(ICallable, title="script setup method", required=False)
	script_teardown = schema.Object(ICallable, title="script teardown method", required=False)
	script_subscriber = schema.Object(ICallable, title="result suscriber", required=False)
	run_time = schema.Int(title="run time in secs", required=False)
	rampup = schema.Int(title="thread rampup", required=False, default=0)
	max_iterations = schema.Int(title="max iterations", required=False)
	use_threads = schema.Bool(title="use threads option", required=False, default=False)
	call_wait_time = schema.Float(title="runner call wait time", required=False, default=0.0)

class IDelegatedContext(IContext):
	group_number = schema.Int(title="runner group number", required=True)
	group_name = schema.TextLine(title="runner group name", required=True)
	runners = schema.Int(title="number of group runners", required=True)
	target = schema.Object(ICallable, title="runner call target [module] method", required=True)
	target_args = schema.Tuple(title="runner arguments", required=False, default=())
	setup = schema.Object(ICallable, title="group setup method", required=False)
	teardown = schema.Object(ICallable, title="group teardown method", required=False)
	
class IRunnerResult(IExternalizable):
	epoch = schema.Float(title="runner epoch", required=False)
	result = schema.Dict(title="runner result", required=False)
	elapsed = schema.Float(title="elapsed time", required=False)
	runner_num = schema.Int(title="runner number", required=True)
	run_time = schema.Dict(title="runner run time", required=True)
	exception = schema.Text(title="exception text", required=False)
	iteration = schema.Int(title="iteration number", required=True)
	group_name = schema.TextLine(title="runner group", required=True)
	custom_timers = schema.Dict(title="runenr custom timers", required=False)

