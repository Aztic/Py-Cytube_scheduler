from sanic import Sanic
from sanic.response import text,json,file,html #response
from libs import socket
from apscheduler.schedulers.background import BackgroundScheduler # scheduler things
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
import json
from datetime import datetime


#Sanic app, gotta go fast
app = Sanic('Gotta go fast')
CONFIG = json.load(open('config','r'))
ACTIVE = json.load(open('active_jobs','r'))
socket = socket.create_socket(room=CONFIG['channel'],user=CONFIG['user'],pw=CONFIG['password'])

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

@app.route("/")
def test(request):
	#return html(open("public/views/index.html",'r').read())
	return file('public/views/index.html')

@app.route("/schedule", methods=["POST"])
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
	app.run(host="localhost",port=8000)
