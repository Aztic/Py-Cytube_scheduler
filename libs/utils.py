from sanic import response
from passlib.hash import pbkdf2_sha256 as pbk
import socket
import sqlite3


LOGIN_ROUTE = "/login"
conn = sqlite3.connect('../info.db')
c = conn.cursor()

#Decorator to force login
def login_required(f):
	def is_logged(x):
		return f(x) if x['session'] else response.redirect(LOGIN_ROUTE)
	return is_logged



def check_user(user,password):
	c.execute('SELECT password FROM users WHERE username=?',(user,))
	result = c.fetchall()
	if not result:
		return False
	return pbk.verify(password,result[0][0])
	
def load_sockects():
	c.execute('SELECT * from user_sockets')
	#content of every line is (owner,user,password,channel)
	users = {}
	
	for line in c.fetchall():
		if line[0] not in users:
			users[line[0]] = []
		socket = socket.create_socket(room=line[3],user=line[1],pw=line[2])
		users[line[0]].append(socket)
	return users

	
#not allowing registers
#def register_user(user,password):
	#Check if user in db
	#if not, register