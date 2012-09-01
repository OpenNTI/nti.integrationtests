from __future__ import print_function, unicode_literals

import MySQLdb as mdb

def show_databases(host, user, password):
	con = mdb.connect(host, user, password)
	with con:
		cur = con.cursor()
		cur.execute("show databases") 
		rows = cur.fetchall()
		result = []
		for row in rows:
			result.append(row[0])
		return result
	
def clean_dbs(host, user, password, prefix='Users'):
	databases = show_databases(host, user, password)
	databases = [n for n in databases if n.startswith(prefix)]
	if databases:
		con = mdb.connect(host, user, password)
		with con:
			cur = con.cursor()
			for db in databases:
				cur.execute("drop database " + db)

def get_users(host, user, password):
	con = mdb.connect(host, user, password)
	with con:
		cur = con.cursor()
		cur.execute("select host, user from mysql.user") 
		rows = cur.fetchall()
		result = []
		for row in rows:
			result.append((row[0], row[1]))
		return result
		
def create_db_user(host, user, password, username='Users', upass='Users'):
	users = get_users(host, user, password)
	found = False
	for host, uname in users:
		if uname == username:
			found = True
			break
	
	if not found:
		upass = upass or username
		con = mdb.connect(host, user, password)
		with con:
			cur = con.cursor()
			cur.execute('create user %s@%s identified by %s', (username, host, upass))
			
	return not found
		
def create_shards(host, user, password, shards=4, prefix='Users', uname='Users'):
	con = mdb.connect(host, user, password)
	with con:
		cur = con.cursor()
		for x in range(0, shards+1):
			db = prefix if x == 0 else prefix + "_" + str(x)
			cur.execute('create database ' + db)
			if uname:
				cur.execute('grant all privileges on ' + db +'.* to ' + uname)
			
def prepare(user, password, host='localhost', shards=4):
	create_db_user(host, user, password)
	clean_dbs(host, user, password)
	create_shards(host, user, password, shards=shards)


	