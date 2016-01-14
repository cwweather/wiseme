# -*- coding: utf-8 -*-
from wiseme import app, socketio


if __name__ == "__main__":
    print '**************************'
    print '**************************'
    print '****** Wiseme start ******'
    print '**************************'
    print '**************************'
    socketio.run(app, port=4990, use_reloader=False)
