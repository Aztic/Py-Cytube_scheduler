from sanic import Sanic
from sanic.response import text,json,file,html,redirect #response
from sanic_session import InMemorySessionInterface #session management
from libs import socket, utils
from apscheduler.schedulers.background import BackgroundScheduler # scheduler things
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
import json
from datetime import datetime


#Manage sessions
session_interface = InMemorySessionInterface()

#Sanic app, gotta go fast
app = Sanic('Gotta go fast')
CONFIG = json.load(open('config','r'))
ACTIVE = json.load(open('active_jobs','r'))
#socket = socket.create_socket(room=CONFIG['channel'],user=CONFIG['user'],pw=CONFIG['password'])
SOCKETS = utils.load_sockets()

#scheduler things
DB_URL = 'sqlite:///info.db'
scheduler = BackgroundScheduler()
scheduler.add_jobstore(SQLAlchemyJobStore(url=DB_URL),alias='info')
scheduler.start()

def clear_done():
	for key in ACTIVE:
		j = scheduler.get_job(key)
		if j is None:
			ACTIVE.pop(key)
	json.dump(ACTIVE,open('active_jobs','w'))

def add_video(url):
	config = {"id": url, "type": "gd", "pos": "end", "duration": 0, "temp": True}
	#try:
	socket.emit("queue",config)
	clear_done()

@app.middleware('request')
async def add_session_to_request(request):
	# before each request initialize a session
	# using the client's request
	await session_interface.open(request)


@app.middleware('response')
async def save_session(request, response):
	# after each request save the session,
	# pass the response to set client cookies
	await session_interface.save(request, response)


@app.route("/test")
def test(request):
	for key in request['session']:
		del request['session'][key]
	return text("nothing")

@app.route("/")
def main_page(request):
	return file('public/views/index.html')

@app.route("/login")
def login(request):
	if request.method == "GET":
		if not request['session']:
			return file('public/views/login.html')
		return redirect("/user")
	else:
		username = request.form.get('username')
		pw = request.form.get('password')
		#check user
		if not utils.check_user(username,pw):
			return redirect('/login')
		if not request['session'].get(username):
			request['session'][username] = 0
		request['session'][username] += 1
		return redirect('/user')

@app.route("/schedule")
@utils.login_required
def handle_form(request):
	#Date/time things
	print(request.form.get('datetime'))
	dt = request.form.get('datetime').split('T')
	date = dt[0].split('-')
	time = dt[1].split(':')
	year,month,day = [int(i) for i in date]
	hour,minute = [int(i) for i in time]

	#url things
	url = request.form.get('url').split('id=')
	if len(url) != 2:
		url = request.form.get('url').split('/')[-2]
	else:
		url = url[1]
	date = datetime(year,month,day,hour,minute,00)

	temp = scheduler.add_job(add_video,trigger='date',args=[url],next_run_time=date,jobstore='info')
	ACTIVE[temp.id] = {'url':url,'date':str(date)}
	json.dump(ACTIVE,open('active_jobs','w'))
	return text("added!")


if __name__ == '__main__':
	app.run(host="localhost",port=8000,debug=True)
