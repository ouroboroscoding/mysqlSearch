#!/usr/bin/python
# coding=utf8
""" SQL Search

Tool to search the structure of an SQL database as opposed to the data
"""

# Import future
from __future__ import print_function, unicode_literals

__author__		= "Chris Nasr"
__copyright__	= "OuroborosCoding"
__license__		= "Apache"
__version__		= "0.1.0"
__maintainer__	= "Chris Nasr"
__email__		= "ouroboroscode@gmail.com"


# Include python modules
from getopt import getopt
import re
import sys

# Include pip modules
import MySQLdb

# Init the default mysql host info
dServer	= {
	"host":			"localhost",
	"port":			3306,
	"db":			"test",
	"user":			"root",
	"passwd":		""
}

# Check command line
tArgs	= getopt(sys.argv[1:], '', ['help', 'host=', 'group='])
dArgs	= dict(tArgs[0])

# If host info was passed
if '--host' in dArgs:

	# Parse the host info
	lHost	= re.search(
		'^(?:([^:@]+)(?::([^@]+))?@)?([^:\/]+)(?::(\d+))?(?:\/(.+))?$',
		dArgs['--host']
	).groups()

	# Overwrite the values that have changed
	if lHost[0]:	dServer['user']		= lHost[0]
	if lHost[1]:	dServer['passwd']	= lHost[1]
	if lHost[2]:	dServer['host']		= lHost[2]
	if lHost[3]:	dServer['port']		= int(lHost[3])
	if lHost[4]:	dServer['db']		= lHost[4]

# Try to get a connection
try:

	# Connect to the server
	oDB		= MySQLdb.connect(**dServer)

	# Turn autocommit on
	oDB.autocommit(True)

	# Get a cursor
	oCur	= oDB.cursor()	# MySQLdb.cursors.DictCursor

	# Select the DB in question
	oCur.execute('USE %s' % dServer['db'])

# If there was an error
except MySQLdb.Error as e:

	# Print the error to stderr
	print(str(e), file=sys.stderr)

	# Return an error
	sys.exit(1)

# Fetch all tables in the DB
oCur.execute('SHOW TABLES')
lTables 	= [l[0] for l in oCur.fetchall()]

# Go through each table
for sTable in lTables:

	# Init loop flags
	bTable	= False

	# Go through each passed search query
	for sQuery in tArgs[1]:

		# If the name matches anything
		if sQuery == sTable or re.match(sQuery, sTable):
			if not bTable:
				print('`%s`' % sTable)
				bTable	= True

	# Fetch the field names
	sSQL	= "SELECT COLUMN_NAME" \
				" FROM INFORMATION_SCHEMA.COLUMNS" \
				" WHERE TABLE_SCHEMA = '%s'" \
				" AND TABLE_NAME = '%s'" % (
		dServer['db'],
		sTable
	)
	oCur.execute(sSQL)
	lFields	= [l[0] for l in oCur.fetchall()]

	# Go through each field
	for sField in lFields:

		# Init loop flags
		bField	= False

		# Go through each passed search query
		for sQuery in tArgs[1]:

			# If the name matches anything
			if sQuery == sField or re.match(sQuery, sField):
				if not bField:
					print('`%s`.`%s`' % (sTable, sField))
					bField	= True

# New line
print('Done')
