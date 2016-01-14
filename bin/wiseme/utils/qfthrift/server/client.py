# coding: utf-8
import time, random
import traceback
import logging
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
import selector

log = logging.getLogger()

class ThriftClientError(Exception):
    pass

class ThriftClient:
    def __init__(self, server, thriftmod, timeout=0, frame_transport=False):
        '''server - 为Selector对象，或者地址{'addr':('127.0.0.1',5000),'timeout':1000}'''
        self.starttime = time.time()
        self.server_selector  = None
        self.server = None
        self.client = None
        self.thriftmod    = thriftmod
        self.frame_transport = frame_transport
        self.raise_except = False  # 是否在调用时抛出异常

        self.timeout = timeout

        if isinstance(server, dict): # 只有一个server
            self.server = [server,]
            self.server_selector = selector.Selector(self.server, 'random')
        elif isinstance(server, list): # server列表，需要创建selector，策略为随机
            self.server = server
            self.server_selector = selector.Selector(self.server, 'random')
        else: # 直接是selector
            self.server_selector = server
        while True:
            if self.open() == 0:
                break

    def open(self):
        starttime = time.time()
        err = ''
        self.transport = None
        #try:
        self.server = self.server_selector.next()
        if not self.server:
            restore(self.server_selector, self.thriftmod)

            self.server = self.server_selector.next()
            if not self.server:
                log.error('server=%s|err=no server!', self.thriftmod.__name__)
                raise ThriftClientError
        addr = self.server['server']['addr']

        try:
            self.transport = TSocket.TSocket(addr[0], addr[1])
            if self.timeout > 0:
                self.transport.setTimeout(self.timeout)
            else:
                self.transport.setTimeout(self.server['server']['timeout'])
            if self.frame_transport:
                self.transport = TTransport.TFramedTransport(self.transport)
            else:
                self.transport = TTransport.TBufferedTransport(self.transport)
            protocol = TBinaryProtocol.TBinaryProtocol(self.transport)

            self.client = self.thriftmod.Client(protocol)
            self.transport.open()
        except Exception, e:
            err = str(e)
            log.error(traceback.format_exc())
            self.server['valid'] = False

            if self.transport:
                self.transport.close()
                self.transport = None
        finally:
            endtime = time.time()
            addr = self.server['server']['addr']
            tname = self.thriftmod.__name__
            pos = tname.rfind('.')
            if pos > 0:
                tname = tname[pos+1:]
            s = 'server=%s|func=open|addr=%s:%d/%d|time=%d' % \
                    (tname,
                    addr[0], addr[1],
                    self.server['server']['timeout'],
                    int((endtime-starttime)*1000000),
                    )
            if err:
                s += '|err=%s' % repr(err)
                log.info(s)
        if not err:
            return 0
        return -1

    def __del__(self):
        self.close()

    def close(self):
        if self.transport:
            self.transport.close()
            self.transport = None
            self.client = None

    def call(self, funcname, *args, **kwargs):
        def _call_log(ret, err=''):
            endtime = time.time()
            addr = self.server['server']['addr']
            tname = self.thriftmod.__name__
            pos = tname.rfind('.')
            if pos > 0:
                tname = tname[pos+1:]

            retstr = str(ret)
            if tname == 'Encryptor' and ret:
                retstr = str(ret.code)
            s = 'server=%s|func=%s|addr=%s:%d/%d|time=%d|args=%s|kwargs=%s' % \
                    (tname, funcname,
                    addr[0], addr[1],
                    self.server['server']['timeout'],
                    int((endtime-starttime)*1000000),
                    args[1:len(args) -1], kwargs)
            if err:
                s += '|ret=%s|err=%s' % (retstr, repr(err))
                log.warn(s)
            else:
                log.info(s)

        starttime = time.time()
        ret = None
        try:
            func = getattr(self.client, funcname)
            ret = func(*args, **kwargs)
        except Exception, e:
            err = str(e)
            _call_log(ret, e)
            log.error(traceback.format_exc())
            if self.raise_except:
                raise
        else:
            _call_log(ret)
        return ret

    def __getattr__(self, name):
        def _(*args, **kwargs):
            return self.call(name, *args, **kwargs)
        return _

def restore(selector, thriftmod, frame_transport=False):
    invalid = selector.not_valid()
    log.debug('invalid server:%s', invalid)
    for server in invalid:
        transport = None
        try:
            log.debug('try restore %s', server['server']['addr'])
            addr = server['server']['addr']
            transport = TSocket.TSocket(addr[0], addr[1])
            transport.setTimeout(server['server']['timeout'])
            if frame_transport:
                transport = TTransport.TFramedTransport(transport)
            else:
                transport = TTransport.TBufferedTransport(transport)
            protocol = TBinaryProtocol.TBinaryProtocol(transport)
            client = thriftmod.Client(protocol)
            transport.open()
            client.ping()
        except:
            log.error(traceback.format_exc())
            log.debug("restore fail: %s", server['server']['addr'])
            continue
        finally:
            if transport:
                transport.close()

        log.debug('restore ok %s', server['server']['addr'])
        server['valid'] = True


#def restore(server_selector):
#    from qfcommon.thriftclient.payprocessor import PayProcessor
#    notvalid = server_selector.not_valid()
#    for server in notvalid:
#        log.debug('try restore %s', server['server']['addr'])
#        try:
#            client = ThriftClient(server['server'], PayProcessor, 100)
#            raise_except = client.raise_except
#            client.raise_except = True
#            client.ping()
#        except:
#            pass
#        else:
#            server['valid'] = True
#            log.debug('restore ok %s', server['server']['addr'])
#
#        client.raise_except = raise_except


def test():
    from qfcommon.thriftclient.payprocessor import PayProcessor
    from qfcommon.base import logger
    global log
    logger.install('stdout')
    log = logger.log
    log.debug('test ...')
    serverlist = [{'addr':('127.0.0.1',4300), 'timeout':1000},
                  {'addr':('127.0.0.1', 4200), 'timeout':1000},
                  ]
    sel = selector.Selector(serverlist)
    for i in range(0, 10):
        client = ThriftClient(sel, PayProcessor)
        client.ping()

    server = sel.next()
    server['valid'] = False

    #log.debug('restore ...')
    #restore(sel)
    print '-'*60
    for i in range(0, 10):
        client = ThriftClient(sel, PayProcessor)
        client.ping()

def test2():
    from qfcommon.thriftclient.encryptor import Encryptor
    from qfcommon.base import logger
    global log
    logger.install('stdout')
    log = logger.log
    log.debug('test ...')
    serverlist = [
            {'addr':('127.0.0.1',4200), 'timeout':1000},
            {'addr':('127.0.0.1',4201), 'timeout':1000},
    ]
    sel = selector.Selector(serverlist)
    client = ThriftClient(sel, Encryptor)
    client.ping2()


def test3():
    from qfcommon.thriftclient.notifier import Notifier
    from qfcommon.base import logger
    global log
    logger.install('stdout')
    log.debug("test framed transport")
    serverlist = [
            {'addr':('172.100.101.151', 15555), 'timeout':1000},
            ]
    sel = selector.Selector(serverlist)
    client = ThriftClient(sel, Notifier, frame_transport=True)
    notify = {
            "notify_url":"http://172.100.101.151:8989/",
            "notify_data": {
                    "orderstatus":"5",
                }
            }
    import json
    ret = client.send_notify(json.dumps(notify))
    log.debug("send notify return:%s", ret)



if __name__ == '__main__':
    test3()


