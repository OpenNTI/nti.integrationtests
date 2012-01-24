#!/usr/bin/env python

import os
import sys
import time
import uuid
import shlex
import curses
import inspect
import argparse
import threading
from datetime import datetime

from websocket_interface import Graph
from websocket_interface import CHANNELS
from websocket_interface import DEFAULT_CHANNEL
from websocket_interface import basic_message_ctx

#########################

_commands = {}

#########################

class User(Graph):
	
	def __str__(self):
		return self.username
	
	@property
	def first_room(self):
		return self.rooms.keys()[0] if self.rooms else None
	
	def chat_recvMessage(self, **kwargs):
		creator = kwargs.get('Creator',  kwargs.get('creator', None))
		cid = kwargs.get('ContainerId',  kwargs.get('containerId', None))
		if cid in self.rooms and creator != self.username:
			super(User, self).chat_recvMessage(**kwargs)
			
	def __call__(self, *args, **kwargs):
		try:
			self.runLoop()
		except Exception, e:
			print e
				
	def ws_close(self, *args, **kwargs):
		if self.connected:
			super(User, self).ws_close(*args, **kwargs)
			print 'Disconnected from %s' % self.host
		
#########################
		
class ArgumentParser(argparse.ArgumentParser):
	
	def error(self, message):
		self.print_usage()
		print message
		raise Exception(message)

def check_attr(ns, attr):
	v = getattr(ns, attr, None)
	return v != None and v
	
#########################

class Command(object):
	
	__alias__ = []
	
	def __init__(self, client=None):
		self.client = client
		self.result = None
		self.namespace = None
		
	def __call__(self, *args, **kwargs):
		self.result = None
		try:
			args = args or []
			ns = self.parse_args(*args)
			if ns:
				self.result = self.execute(ns)
				return True
		except Exception, e:
			self.result = None
			print e #sys.exc_info()
		
		return False
	
	@property
	def parser(self):
		return self.__parser__

	def parse_args(self, *args):
		try:
			self.namespace = self.parser.parse_args(args=args)
			return self.namespace
		except:
			self.namespace = None
			pass
		
		return None
	
	def execute(self, ns):
		pass
	
#------------------------------

class Open(Command):
	
	__parser__ = ArgumentParser(description='Open a connection', add_help=False, prog="open")
	__parser__.add_argument('-t', '--host', type=str, dest="host", help='Set the ds host', default="localhost")
	__parser__.add_argument('-o', '--port', type=int, dest="port", help='Set the ds port', default=8080)
	__parser__.add_argument('-u', '--user', type=str, dest="user", help='Set the connection user', required=True)
	__parser__.add_argument('-p', '--password', type=str, dest="password", help='Set the connection password', default="temp001")
		
	def execute(self, ns):
		
		if self.client:
			self.client.ws_close()
			
		self.client = User(	username=ns.user, host=ns.host, port=ns.port, \
							password=ns.password, message_context=basic_message_ctx)
		
		try:
			self.client.ws_connect()
			print "Connected as '%s' to %s:%s" % (ns.user, ns.host, ns.port) 
		except Exception, e:
			self.client = None
			raise e
		
		t_t=threading.Thread(target=self.client)
		t_t.start()
	
#------------------------------

class EnterRoom(Command):
	
	__alias__ = ['enter', 'start_chat', 'join']
	
	__parser__ = ArgumentParser(description='Connect to a room', add_help=False)
	__parser__.add_argument('-o', '--occupants', type=str, dest="Occupants", help='Set the room occupants', nargs='+')
	__parser__.add_argument('-t', '--inreplyto', type=str, dest="inReplyTo", help='Set the inReplyTo id' )
	__parser__.add_argument('-r', '--references', type=str, dest="references", help='Set the references id')
	__parser__.add_argument('-c', '--container', type=str, dest="ContainerId", help='Set the container id')
		
	def __init__(self, *args, **kwargs):
		super(EnterRoom, self).__init__(*args, **kwargs)
		self.saved_chat_enteredRoom = None
		self.event = threading.Event()
		
	def _chat_enteredRoom(self, **kwargs):
		room = self.saved_chat_enteredRoom(**kwargs)
		print "Entered room '%s'" % room
		self.event.set()
		
	def parse_args(self, *args):
		return super(EnterRoom, self).parse_args(*args) if args else argparse.Namespace()
			
	def execute(self, ns):
		if not self.client or not self.client.connected:
			raise Exception("Not connected") 
		elif not check_attr(ns, 'ContainerId') and not check_attr(ns, 'Occupants'):
			raise Exception("Must specify either a container or ocuppants")
		
		params = dict(ns.__dict__)
		if not 'ContainerId' in params or not params['ContainerId']:
			params['ContainerId'] = str(uuid.uuid4())
		
		if 'Occupants' in params and params['Occupants']:
			o = set([self.client.username] + params['Occupants'])
			params['Occupants'] = list(sorted(o))
		
		self.saved_chat_enteredRoom = self.client.chat_enteredRoom
		try:
			self.client.chat_enteredRoom = self._chat_enteredRoom
			self.client.enterRoom(**params)
			
			self.event.wait(60)
			if not self.event.is_set():
				raise Exception("Could not enter room")
		finally:
			self.client.chat_enteredRoom = self.saved_chat_enteredRoom

class ExitRoom(Command):
	
	__alias__ = ['leave', 'stop_chat']
	
	__parser__ = ArgumentParser(description='Leave a room', add_help=False)
	__parser__.add_argument('-o', '--room', type=str, dest="room_id", help='Set the room id')
				
	def parse_args(self, *args):
		return super(ExitRoom, self).parse_args(*args) if args else argparse.Namespace()
			
	def execute(self, ns):
		if not self.client or not self.client.connected:
			raise Exception("Not connected") 
		elif not check_attr(ns, 'room_id'):
			ns.room_id = self.client.first_room
		
		if not ns.room_id:
			raise Exception('Must specify a room id')
		elif not ns.room_id in self.client.rooms:
			raise Exception('Invalid room id')
		
		self.client.exitRoom(ns.room_id)
		self.client.rooms.pop(ns.room_id, None)
			
#------------------------------

class Send(Command):
	
	__alias__ = ['post']
	
	__parser__ = ArgumentParser(description='Send/Post a message', add_help=False)
	__parser__.add_argument('-m', '--message', type=str, dest="message", help='Set the room message', required=True)
	__parser__.add_argument('-o', '--room', type=str, dest="ContainerId", help='Set the room id')
	__parser__.add_argument('-t', '--inreplyto', type=str, dest="inReplyTo", help='Set the inReplyTo id')
	__parser__.add_argument('-r', '--recipients', type=str, dest="recipients", help='Set the recipients', nargs='*')
	__parser__.add_argument('-c', '--channel', help='Set the channel', type=str, dest="channel",\
							 default=DEFAULT_CHANNEL, choices=CHANNELS)
						
	def execute(self, ns):
		if not self.client or not self.client.connected:
			raise Exception("Not connected") 
		elif not ns.ContainerId:
			if not self.client.rooms:
				raise Exception("Must specify a room id")
			else:
				ns.ContainerId = self.client.first_room
				
			self.client.postMessage(**ns.__dict__)
		
class Retrieve(Command):
	
	__alias__ = ['recv', 'get']	
	__parser__ = ArgumentParser(description='Display received messages', add_help=False)
	__parser__.add_argument('-a', '--all', dest="all", help='Show all messages', action="store_true", default=False)
	__parser__.add_argument('-s', '--shadowed',  dest="shadowed", help='Show shadowed messages', action="store_true", default=False)
	__parser__.add_argument('-m', '--moderated', dest="moderated", help='Show moderated messages', action="store_true", default=False)
	
	def __init__(self, *args, **kwargs):
		super(Retrieve, self).__init__(*args, **kwargs)
				
	def _display(self, messages):
		for i, m in enumerate(messages):
			print "%s. message='%s', from='%s', at='%s', channel='%s'" % \
				  (i, m.text, m.creator, datetime.fromtimestamp(m.lastModified), m.channel)

	def execute(self, ns):
		if not self.client or not self.client.connected:
			raise Exception("Not connected") 
		
		messages = self.client.get_received_messages()
		self._display(messages)
		
		if ns.all or ns.shadowed:
			messages = self.client.get_shadowed_messages()
			if messages:
				print 'Shadowed Messages'
				self._display(messages)
				
		if ns.all or ns.moderated:
			messages = self.client.get_moderated_messages()
			if messages:
				print 'Moderated Messages'
				self._display(messages)
						
#------------------------------

class Rooms(Command):
	
	__parser__ = ArgumentParser(description='Display room information', add_help=False)
		
	def parse_args(self, *args):
		return argparse.Namespace()
			
	def execute(self, ns):
		if not self.client or not self.client.connected:
			print 'Not connected'
		else:
			for i, r in enumerate(list(self.client.rooms.itervalues())):
				print "%s. id='%s', container='%s', occupants='%s'" % (i, r.ID, r.containerId, r.occupants)
			
#------------------------------

class Help(Command):
	
	__parser__ = ArgumentParser(description='Provides command help', add_help=False)
	__parser__.add_argument('command', help='Specify the command to get help for', action="store")
	
	def parse_args(self, *args):
		return super(Help, self).parse_args(*args) if args else argparse.Namespace()
		
	def execute(self, ns):
		if not ns or not hasattr(ns, 'command'):
			print "available commands"
			print sorted(_commands.keys())
		elif not ns.command in _commands:
			print "'%s' is unknown command" % ns.command
		else:
			clazz = _commands[ns.command]
			if hasattr(clazz, 'parser'):
				print clazz.__parser__.description
				clazz.__parser__.prog = ns.command
				clazz.__parser__.print_usage()
			else:
				print "no help provided for '%s'" % ns.command
		
#------------------------------
		
class Wait(Command):
	
	__parser__ = ArgumentParser(description='Wait for a time in secs', add_help=False)
	__parser__.add_argument('seconds', help='Specify the time to wait in secs', type=int, action="store")
		
	def execute(self, ns=None):
		if ns.seconds > 0 and ns.seconds <= 3600:
			print 'Waiting %s seconds' % ns.seconds
			time.sleep(ns.seconds)
		else:
			raise Exception("Invalid number of seconds [1,3600]")
		
#------------------------------
		
class Exit(Command):
	
	__alias__ = ['terminate', 'bye']
	__parser__ = ArgumentParser(description='Terminate session', add_help=False)
	
	def __call__(self, *args, **kwargs):
		self.execute()
		
	def execute(self, ns=None):
		if self.client:
			self.client.ws_close()
		sys.exit(0)
				
#########################

def capture_commands():
	for k, v in dict(globals()).items():
		if 	inspect.isclass(v) and issubclass(v, Command) and hasattr(v, '__alias__') and \
			v != Command:
			
			register = [k.lower()] + v.__alias__
			for r in register:
				_commands[r] = v

capture_commands()
		
#########################
	
def parse_and_execute(var, client=None):
	command = None
	status = False
	args = shlex.split(var) 
	if args:
		cmd_name = args[0]
		if not cmd_name in _commands:
			print "'%s' is an uknown command" % cmd_name
		else:
			args = args[1:]
			clazz = _commands[cmd_name]
			command = clazz(client)
			command.parser.prog = cmd_name
			status = command(*args)
	return (command, status)

def excute_command_file(cmd_file):
	if not os.path.exists(cmd_file) or not os.path.isfile(cmd_file):
		raise Exception('%s is an invalid command file')
	
	print "Executing commands in '%s'" % cmd_file
	
	client = None
	with open(cmd_file, 'r') as source:
		for line in source:
			print line
			command, status = parse_and_execute(line, client)
			if status:
				client = command.client if command else client
			else:
				break
				
def main(args=None):
	args = args or sys.argv[1:]
	if not args:
		client = None
		while True:
			var = raw_input(">>> ")
			command, _ = parse_and_execute(var, client)
			client = command.client if command else client
	else:
		excute_command_file([0])
		

def inputing(screen):
	
	screen.move(screen.getmaxyx()[0]-1, 0)
	screen.addstr(screen.getmaxyx()[0]-1, 0, ">>> ")
	
	min_x = 4
	line = []
	screen.scrollok(True)
	while True:
		try:
			char = screen.getch()
			if char == 127:
				y, x = screen.getyx()
				if x > min_x:
					x=x-1
					screen.move(y,x)
					screen.echochar(' ')
					screen.move(y,x)
			elif char == 10:
				y = screen.getyx()[0]
				if y+1 >= screen.getmaxyx()[0]:
					screen.scroll()
					screen.move(y, 0)
				else:
					screen.move(y+1, 0)
				y,x = screen.getyx()
				screen.addstr(y,x,">>> ")
			
			elif char == 4:
				break
			elif char >=32 and char < 256:
				line.append(chr(char))
				screen.echochar(char)
		except KeyboardInterrupt:
			curses.flushinp()
			screen.scroll()
			screen.move(screen.getmaxyx()[0]-1, 0)
			screen.addstr(screen.getmaxyx()[0]-1,0,"KeyboardInterrupt")
			screen.scroll()
			screen.move(screen.getmaxyx()[0]-1, 0)
			screen.addstr(screen.getmaxyx()[0]-1,0, ">>> ")
	
def use_curses():
	curses.wrapper(inputing)

if __name__ == '__main__':
	main()
