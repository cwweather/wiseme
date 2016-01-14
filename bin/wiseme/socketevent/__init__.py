# -*- coding: utf-8 -*-
from .. import socketio

@socketio.on("test")
def test(msg):
    print('received test: ' + str(msg))