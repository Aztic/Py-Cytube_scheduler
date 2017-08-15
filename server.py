from sanic import Sanic
from sanic_jinja2 import SanicJinja2
from sanic.response import text,json,file,html,redirect #response
from sanic_session import InMemorySessionInterface #session management
from libs import utils
from apscheduler.schedulers.background import BackgroundScheduler # scheduler things
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
import json
import os
from datetime import datetime

#Manage sessions
session_interface = InMemorySessionInterface()

#Sanic app, gotta go fast
app = Sanic()
jinja = SanicJinja2(app)
with open('active_jobs','r') as active:
	ACTIVE = json.load(active)
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
				del ACTIVE[user][key]
				with open('active_jobs','w') as active:
					json.dump(ACTIVE,active)


def add_video(url,user):
	config = {"id": url, "type": "gd", "pos": "end", "duration": 0, "temp": True}
	SOCKETS[user].emit("queue",config)
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


#Static files handler
@app.route('public/<type:string>/<filename:string>',methods=['GET'])
def return_static(request,type,filename):
	return file(os.path.join(os.getcwd(),'public',type,filename))

#Socket stuff section
@app.route('user/deletesocket',methods=['DELETE'])
@utils.login_required
def delete_socket(request):
	user = [*request['session']][0]
	if not utils.valid_token(request['session'][user]):
		return json({'status':401,'desc':'forbidden'})
	utils.delete_socket(user)
	del SOCKETS[user]
	return text("success")

@app.route('user/createsocket',methods=['POST'])
@utils.login_required
def create_socket(request):
	user = [*request['session']][0]
	if not utils.valid_token(request['session'][user]):
		return json({'status':401,'desc':'forbidden'})
	username = request.form.get('username')
	password = request.form.get('password')
	channel = request.form.get('channel')
	SOCKETS[user] = utils.create_user_socket(user,username,password,channel)
	return redirect('/user')

@app.route('user/deletejob',methods=['DELETE'])
@utils.login_required
def delete_job(request):
	user = [*request['session']][0]
	if not utils.valid_token(request['session'][user]):
		return json({'status':401,'desc':'forbidden'})
	job_id = request.args.get('id')
	scheduler.remove_job(job_id)
	del ACTIVE[user][job_id]
	json.dump(ACTIVE,open('active_jobs','w'))
	return text("success")

#Root page
@app.route("/")
def main_page(request):
	return jinja.render('ind.html', request, username=utils.get_user(request))

#Login page
@app.route("/login",methods=['GET','POST'])
def login(request):
	if request.method == "GET":
		if not request['session']:
			return jinja.render('login.html',request)
		return redirect("/user")
	else:
		username = request.form.get('username')
		pw = request.form.get('password')
		#check user
		if not utils.check_user(username,pw):
			return text("Invalid")
			return redirect('/login')
		request['session'][username] = utils.user_token(username)
		return redirect('/')

@app.route("/logout",methods=['POST'])
@utils.login_required
def logout(request):
	request['session'].clear()
	return redirect('/')

@app.route("/register",methods=['GET','POST'])
def register(request):
	if request.method == "GET":
		return jinja.render('register.html',request)
	else:
		username = request.form.get('username')
		email = request.form.get('email')
		pw = request.form.get('password')
		resp = utils.register_user(username,email,pw)
		return text(resp)

#Schedule things
@app.route("/schedule",methods=['GET','POST'])
@utils.login_required
def handle_form(request):
	user = utils.get_user_info([*request['session']][0])
	if request.method == "GET":
		if user['socket']:
			return jinja.render('schedule.html',request,username=user['name'])
		return redirect('/user')
	#Date/time things
	dt = request.form.get('datetime').split('T')
	date = dt[0].split('-')
	time = dt[1].split(':')
	year,month,day = [int(i) for i in date]
	hour,minute = [int(i) for i in time]
	repeat = True if request.form.get('checkbox') is not None else False
	#url things
	url = request.form.get('url').split('id=')
	if len(url) != 2:
		url = request.form.get('url').split('/')[-2]
	else:
		url = url[1]
	date = datetime(year,month,day,hour,minute,00)
	#user = [*request['session']][0]
	description = request.form.get('description')

	temp = scheduler.add_job(add_video,trigger='date',args=[url,user['name']],next_run_time=date,jobstore='info')

	if user['name'] not in ACTIVE:
		ACTIVE[user['name']] = {}
	ACTIVE[user['name']][temp.id] = {'url':url,'date':str(date),'type':'add video','description':description}
	json.dump(ACTIVE,open('active_jobs','w'))
	return redirect("/user")

@app.route('/user',methods=['GET'])
@utils.login_required
def user_profile(request):
	#Get all the user information
	user = utils.get_user_info([*request['session']][0])
	jobs = ACTIVE[user['name']] if user['name'] in ACTIVE else None
	return jinja.render('user.html',request,username=user['name'],user=user,jobs=jobs)


if __name__ == '__main__':
	app.run(host="127.0.0.1",port=8000,debug=True)
