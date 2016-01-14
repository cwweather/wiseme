# -*- coding: utf-8 -*-
import os
import sys
from flask import Flask, request_finished, request_started
from flask.ext.socketio import SocketIO
from flask.ext.session import Session
from settings import getenvconf
from dbs import init_mysqldb, init_mmwddb, init_mongo, init_postgre
from werkzeug.contrib.fixers import ProxyFix
from utils.delivery import DeliveryHandler

# Add PATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# default encoding
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

# 获取环境变量
env = os.getenv('env')
if env:
    env = env.lower()
app = Flask(__name__)
conf = getenvconf(env)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = conf.SESSION_DIR
app.config.from_object(conf)
app.mysqldb = init_mysqldb(conf.MYSQL_MAIN)
app.mmwddb = init_mmwddb(conf.MYSQL_MMWD)
app.neardb = init_mmwddb(conf.MYSQL_NEAR)
app.mongodb = init_mongo(conf.MONGODB_HOST_R, conf.MONGODB_PORT_R)
app.psql = init_postgre(conf.PSQL_DB, conf.PSQL_USER, conf.PSQL_PW, conf.PSQL_HOST)
app.mongodb_for_write = init_mongo(conf.MONGODB_HOST_W, conf.MONGODB_PORT_W)
app.deliveryhandler = DeliveryHandler(app_code=conf.DELIVERY_APP_CODE, server_key=conf.DELIVERY_SERVER_KEY,
                                      host=conf.DELIVERY_HOST, port=conf.DELIVERY_PORT)
from urls import urlsmap
urlsmap(app)
# 支持Gunicorn
app.wsgi_app = ProxyFix(app.wsgi_app)
Session(app)
socketio = SocketIO(app)
#from socketevent import test
from socketevent import showtime


from utils.qfrequest import send_remote_log_tail, handle_before_request
request_started.connect(handle_before_request, app)
request_finished.connect(send_remote_log_tail, app)