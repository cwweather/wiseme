# coding: utf-8
from server.client import ThriftClient


def thrift_callex(server, thriftmod, funcname, *args, **kwargs):
    client = ThriftClient(server, thriftmod)
    client.raise_except = True

    return client.call(funcname, *args, **kwargs)