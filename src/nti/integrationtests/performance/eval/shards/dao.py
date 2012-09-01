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
	
def clean_dbs(host, user, password, prefix='Users_'):
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
		
def create_user(host, user, password, username='Users', upassword='Users'):
	users = get_users(host, user, password)
	found = False
	for host, uname in users:
		if uname == username:
			found = True
			break
	
	if not found:
		upassword = upassword or username
		con = mdb.connect(host, user, password)
		with con:
			cur = con.cursor()
			cur.execute('create user %s@%s identified by %s', (username, host, upassword))
			
	return not found
		
if __name__ == '__main__':
	print(create_user('localhost', 'root', 'saulo213'))
	