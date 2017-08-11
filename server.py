from sanic import Sanic
from sanic_jinja2 import SanicJinja2
from routes import api,page
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
app = Sanic()
jinja = SanicJinja2(app)
#Add routes
#api.routes(app)
#page.routes(app)
CONFIG = json.load(open('config','r'))
ACTIVE = json.load(open('active_jobs','r'))
#socket = socket.create_socket(room="https://cytu.be/r/whyamicreatingachannel",user="aztic",pw="Haishipe0R")
SOCKETS = utils.load_sockets()

#scheduler things
DB_URL = 'sqlite:///info.db'
scheduler = BackgroundScheduler()
scheduler.add_jobstore(SQLAlchemyJobStore(url=DB_URL),alias='info')
scheduler.start()


def clear_done():
	for user in ACTIVE:
		for key in ACTIVE[user]:
			status = scheduler.get_job(key)
			if status is None:
				ACTIVE.pop(key)
	json.dump(ACTIVE,open('active_jobs','w'))


def add_video(url,user,inf):
	config = {"id": url, "type": "gd", "pos": "end", "duration": 0, "temp": True}
	#try:
	SOCKETS[user][inf]['socket'].emit("queue",config)
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


#Root page
@app.route("/")
def main_page(request):
	#rint(session_interface.user)
	return jinja.render('ind.html', request, user=utils.is_user_active(request))
	#return file('templates/ind.html')

#Login page
@app.route("/login")
def login(request):
	if request.method == "GET":
		if not request['session']:
			return jinja.render('login.html',request,user=utils.is_user_active(request))
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

#Schedule things
@app.route("/schedule")
@utils.login_required
def handle_form(request):
	if request.method == "GET":
		return redirect('\\')
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
	user = [i for i in request['session']][0]

	temp = scheduler.add_job(add_video,trigger='date',args=[url,user,info],next_run_time=date,jobstore='info')
	if user not in ACTIVE:
		ACTIVE[user] = {}
	ACTIVE[user][temp.id] = {'url':url,'date':str(date)}
	json.dump(ACTIVE,open('active_jobs','w'))
	return text("added!")

@app.route('/user',methods=['GET'])
@utils.login_required
def user_profile(request):
	return jinja.render('user.html',request,jobs=ACTIVE[user])


if __name__ == '__main__':
	app.run(host="127.0.0.1",port=8000,debug=True)
