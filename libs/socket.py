import requests
from socketIO_client import SocketIO

def create_socket(room,user,pw):
	protocol = 'https'
	channel = room.split('/')[-1]
	socket = SocketIO(get_server(protocol,channel))
	socket.emit('joinChannel',{'name':channel})
	socket.emit('login',{'name':user,'pw':pw})
	return socket

def get_server(protocol,room):
	secure = True if protocol == 'https' else False
	req = requests.get('{}://cytu.be:{}/socketconfig/{}.json'.format(protocol,443 if secure else 80,room))
	if req.status_code == 200:
		servers = req.json()
		for server in servers['servers']:
			if server["secure"]:
				return server["url"]
	return False
