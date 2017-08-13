# Py-Cytube_scheduler
A scheduler bot for [cytu.be](https://cytu.be) that uses [Sanic](https://github.com/channelcat/sanic) as backend. Was inspired by this [cytube bot](https://github.com/nuclearace/CytubeBot)

## Requirements
If you want to install them manually, go ahead. If not, use `pip install -r requirements.txt`.
- [Sanic](https://github.com/channelcat/sanic) ~~GOTTA GO FAST~~
- [apscheduler](https://pypi.python.org/pypi/APScheduler)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [requests](http://docs.python-requests.org/en/master/)
- [socketIO-client3](https://pypi.python.org/pypi/socketIO-client3)
- [SQLite3](https://www.sqlite.org/)

## Usage
- Configure the server with your cytu.be username, password and desired room. Put that info in `config`
- Run the server
```
python3 server.py
```
- Go to `http://locahost:8000`
- Use it

## Not using database or using another
If you want you can not use the database or just user another, like Postgresql or MySQL.
### If you want to use another
- Change `DB_URL` with the url to your database
### If you want to not use a database
I recommend to use one, so the scheduler wont delete de jobs everytime the server crashes.
- Avoid importing `SQLAlchemyJobStore`
- Delete this line
```python
scheduler.add_jobstore(SQLAlchemyJobStore(url=DB_URL),alias='info')
```
- Delete 
```python
jobstore='info' 
```
from
```python
scheduler.add_job() 
```

## TODO
- Multiple sockets per user
- Multiple commands per user

## License
Apache 2.0
