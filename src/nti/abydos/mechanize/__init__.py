#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from .. import toExternalObject

boolean_states = { u'1': True, 'y':True, u'yes': True, u'true': True, u'on': True,
				   u'0': False, 'n':False, u'no': False, u'false': False, u'off': False}
