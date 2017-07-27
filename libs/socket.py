import requests
from socketIO_client import SocketIO
#socket = SocketIO('https://lax1.cytu.be:10443')

#Scheduler things


#datetime.datetime(year,month,day,hour,minute,second)


#join to selected channel
#socket.emit('joinChannel',{'name':'le_room'})
#login
#socket.emit('login',{'name':'le_username','pw':'le_pw'})
#Add to queue
#socket.emit("queue",{"le":"dictionary"})

#json = {"id": id, "type": type, "pos": pos, "duration": 0, "temp": temp}

def create_socket(room,user,pw):
	protocol = room.split(':')[0]
	channel = room.split('/')[-1]
	socket = SocketIO(get_server(protocol,channel))
	socket.emit('joinChannel',{'name':channel})
	socket.emit('login',{'name':user,'pw':pw})
	return socket

def get_server(protocol,room):
	secure = True if protocol == 'https' else False
	options = {'host':'cytu.be','port':443,'path':'/socketconfig/{}.json'.format(room),'timeout':20}
	req = requests.get('{}://cytu.be:{}/socketconfig/{}.json'.format(protocol,443 if secure else 80,room))
	if req.status_code == 200:
		servers = req.json()
		for server in servers['servers']:
			if server["secure"]:
				return server["url"]
	return False