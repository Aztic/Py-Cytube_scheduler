# Py-Cytube_scheduler
A scheduler bot for [cytu.be](https://cytu.be) that uses [Sanic](https://github.com/channelcat/sanic) as backend.

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

## TODO
- User login
- Multiple sockets per user
- Multiple commands per user
- List of `todo` jobs
