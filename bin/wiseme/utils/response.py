# -*- coding: utf-8 -*-
"""
返回处理
"""
import json
from flask import make_response
import datetime
from misc import DATE_FORMAT, DATETIME_FORMAT


class QFRET:
    OK = "0000"
    DBERR = "2000"
    THIRDERR = "2001"
    SESSIONERR = "2002"
    DATAERR = "2003"
    IOERR = "2004"
    LOGINERR = "2100"
    PARAMERR = "2101"
    USERERR = "2102"
    ROLEERR = "2103"
    REQERR = "2200"
    IPERR = "2201"
    NODATA = "2300"
    DATAEXIST = "2301"
    UNKOWNERR = "2400"


# 增强型json编码器
class ExtendedEncoder(json.JSONEncoder):
    def default(self, o):
        if type(o) == datetime.date:
            return o.strftime(DATE_FORMAT)
        elif type(o) == datetime.datetime:
            return o.strftime(DATETIME_FORMAT)
        else:
            return json.JSONEncoder(self, o)


error_map = {
    QFRET.OK: u"成功",
    QFRET.DBERR: u"数据库查询错误",
    QFRET.THIRDERR: u"第三方系统错误",
    QFRET.SESSIONERR: u"用户未登录",
    QFRET.DATAERR: u"数据错误",
    QFRET.IOERR: u"文件读写错误",
    QFRET.LOGINERR: u"用户登录失败",
    QFRET.PARAMERR: u"参数错误",
    QFRET.USERERR: u"用户不存在或未激活",
    QFRET.ROLEERR: u"用户身份错误",
    QFRET.REQERR: u"非法请求或请求次数受限",
    QFRET.IPERR: u"IP受限",
    QFRET.NODATA: u"无数据",
    QFRET.DATAEXIST: u"数据已存在",
    QFRET.UNKOWNERR: u"未知错误",
}


def error(errcode, respmsg='', resperr='', data=None, escape=False, encoder=ExtendedEncoder, param=None):
    if not respmsg:
        respmsg = error_map[errcode]
    if not resperr:
        resperr = respmsg
    if not data:
        data = {}
    ret = {"respcd": errcode, "respmsg": respmsg, "resperr": resperr, "data": data}
    res = make_response(json.dumps(ret, ensure_ascii=escape, cls=encoder, separators=(',', ':')))
    res.headers['Content-Type'] = 'application/json; charset=UTF-8'
    return res


def success(data, respmsg='', resperr='', escape=False, encoder=ExtendedEncoder, param=None):
    if not respmsg:
        respmsg = "成功"
    ret = {"respcd": "0000", "respmsg": respmsg, "resperr": resperr, "data": data}
    res = make_response(json.dumps(ret, ensure_ascii=escape, cls=encoder, separators=(',', ':')))
    res.headers['Content-Type'] = 'application/json; charset=UTF-8'
    return res
