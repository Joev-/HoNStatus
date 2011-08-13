import sys, MySQLdb
import log

database = None

def connect(hostname, username, password, dbname):
	global database
	try:
		database = MySQLdb.connect(host = hostname, user = username, passwd = password, db = dbname, charset="utf8",use_unicode = True) 
	except MySQLdb.Error, e:
		log.error("Error %d: %s" % (e.args[0], e.args[1]))
		sys.exit(1)

def query(query, args=[]):
	cursor = database.cursor()
	cursor.execute(query, args)
	result = cursor.fetchall()
	cursor.close()
	return result

def execute(query, args=[]):
	cursor = database.cursor()
	affected = cursor.execute(query, args)
	cursor.close()
	return affected
