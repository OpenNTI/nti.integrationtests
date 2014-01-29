#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

default_timeout = None

def get_default_timeout():
    """
    Return the global timeout setting to connect.
    """
    return default_timeout

def set_default_timeout(timeout):
    """
    Set the global timeout setting to connect.
    """
    global default_timeout
    default_timeout = timeout

class SocketIOException(Exception):
    pass

class ConnectionClosedException(SocketIOException):
    pass

class SocketIOSocket(object):

    WS_CONNECT = b'1::'

    def __init__(self):
        self.connected = False

    def connect(self, url, *args, **kwargs):
        """
        Connect to url.
        """
        raise NotImplementedError()

    def send(self, payload):
        """
        Send the data as string. payload must be utf-8 string or unicoce.
        """
        raise NotImplementedError()

    def recv(self):
        """
        Reeive utf-8 string data from the server.
        """
        raise NotImplementedError()

    def close(self):
        """
        Close Socket object
        """
        raise NotImplementedError()

    def heartbeat(self):
        """
        send a heartbeat
        """
        raise NotImplementedError()

    def isHeartBeat(self, msg):
        """
        check if the specified message is a heartbeat or noop
        """
        raise NotImplementedError()

    is_heart_beat = isheartbeat = isHeartBeat  # BWC

    @classmethod
    def connect_to_server(cls, host, port, username, password, is_secure=False,
                          timeout=default_timeout, **kwargs):
        raise NotImplementedError()

