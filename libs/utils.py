from sanic import response
from passlib.hash import pbkdf2_sha256 as pbk
from random import choices
import string
from . import socket
import sqlite3

LOGIN_ROUTE = "/login"
conn = sqlite3.connect('info.db')
c = conn.cursor()


def is_user_active(request):
	return True if request['session'] else False

#Return the active user, stored in the session
def get_user(request):
	return False if not request['session'] else [*request['session']][0]


#Decorator to force login
def login_required(f):
	def is_logged(x):
		return f(x) if x['session'] else response.redirect(LOGIN_ROUTE)
	return is_logged

def valid_token(token):
	c.execute('SELECT * FROM users WHERE token=?',(token,))
	data = c.fetchall()
	return True if data else False

#Check if it's a valid user information
def check_user(user,password):
	c.execute('SELECT password FROM users WHERE user=?',(user,))
	result = c.fetchall()
	if not result:
		return False
	return pbk.verify(password,result[0][0])

def generate_token(quantity):
	return ''.join(choices(string.ascii_uppercase + string.ascii_lowercase + string.digits,k=quantity))

#not allowing registers
def register_user(user,email,password):
	resp = {'Success':True}
	c.execute('SELECT password FROM users WHERE user=?',(user,))
	result = c.fetchall()
	if result:
		resp['Success'] = False
		resp['error'] = "invalid user"
	else:
		c.execute('INSERT INTO users(user,email,password,token) VALUES (?,?,?,?)',
			(user,email,pbk.hash(password),generate_token(50)))
		conn.commit()
	return resp


#Load sockets from database	
def load_sockets():
	c.execute('SELECT * FROM user_sockets')
	#content of every line is (owner,user,password,channel)
	users = {}
	
	for line in c.fetchall():
		if line[0] not in users:
			users[line[0]] = []
		sk = socket.create_socket(room=line[3],user=line[1],pw=line[2])

		users[line[0]] = sk
	return users

def create_user_socket(owner,user,password,channel):
	c.execute('DELETE FROM user_sockets where owner=?',(owner,))
	c.execute('INSERT INTO user_sockets (owner,user,password,channel) VALUES (?,?,?,?)',(owner,user,password,channel))
	conn.commit()
	return socket.create_socket(room=channel,user=user,pw=password)

def delete_socket(user):
	c.execute('DELETE FROM user_sockets where owner=?',(user,))
	conn.commit()


def get_user_info(user):
	c.execute('SELECT * FROM users where user=?',(user,))
	socket = {}
	data = c.fetchall()
	user = data[0][1]
	c.execute('SELECT * FROM user_sockets where user=?',(user,))
	data = c.fetchall()
	if data:
		socket = {'username':data[0][1],'channel':data[0][3]}
	return {'name':user,'socket':socket}

def get_active_jobs(token):
	select
	return False

#Return user token
def user_token(user):
	c.execute('SELECT token FROM users WHERE user=?',(user,))
	return c.fetchall()[0][0]
