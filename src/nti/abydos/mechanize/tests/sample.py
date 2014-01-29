#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from nti.abydos.mechanize import interfaces as mc_interfaces

def script_setup(context):
    context.script_setup = True

def script_teardown(context):
    context.script_teardown = True

def setup(context):
    context.setup = True

def teardown(context):
    context.teardown = True

def creation(*args, **kwargs):
    return 1

@interface.implementer(mc_interfaces.IResultListener)
class _listener(object):

    def open(self, context):
        context.opened = True

    def __call__(self, result):
        result.listened = True

    def close(self, context):
        context.closed = True
