# -*- coding: utf-8 -*-
"""
日期
"""
import re
import json
import types
import time
import datetime
import random

# 日期格式
DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

date_pattern = re.compile("\d+\-\d+\-\d+")
time_pattern = re.compile("\d+-\d+-\d+ \d+:\d+:\d+")


def time2date(timestamp):
    """
    将时间戳转换成日期
    :param timestamp: 时间戳 eg:1426231925.17
    :return: datetime eg: 2015-03-13 15:33:00.598979
    """
    return datetime.datetime.fromtimestamp(time.time())


def get_match_pattern(dstr):
    fm = TIME_FORMAT
    if time_pattern.search(dstr):
        fm = TIME_FORMAT
    elif date_pattern.search(dstr):
        fm = DATE_FORMAT
    return fm


def now2str(ftype=TIME_FORMAT):
    return datetime2str(datetime.datetime.now(), ftype)


def datetime2str(t, ftype=TIME_FORMAT):
    return t.strftime(ftype)


def timestamp2str(ts):
    return datetime2str(datetime.datetime.fromtimestamp(ts))


def timestamp2datestr(ts):
    return datetime2str(datetime.datetime.fromtimestamp(ts), ftype=DATE_FORMAT)


def str2datetime(dstr, fm=None):
    if not fm:
        fm = get_match_pattern(dstr.strip())
    return datetime.datetime.strptime(dstr, fm)


def date2timestamp(t):
    dstr = datetime2str(t, TIME_FORMAT)
    return time.mktime(time.strptime(dstr, TIME_FORMAT))


def str2timestamp(dstr, fm=None):
    if not fm:
        fm = get_match_pattern(dstr.strip())
    return time.mktime(time.strptime(dstr, TIME_FORMAT))


def minus_seconds(d1, d2):
    minus = d1 - d2
    days = minus.days
    seconds = (days * 3600 * 24) + minus.seconds
    return seconds


def get_day_begin(ts=time.time()):
    """
    获取时间戳ts当天的起始时间戳
    """
    return int(time.mktime(time.strptime(time.strftime('%Y-%m-%d', time.localtime(ts)), '%Y-%m-%d')))


def get_day_begin_datetimestr():
    """
    获取当天起始时间字符串
    """
    time_begin = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
    return time_begin.strftime(TIME_FORMAT)


def get_datetime_of_day(n=0):
    """
    获取n天后的那一天的起始时间戳
    n < 0, n天前；n > 0, n天后
    """
    time_begin = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
    if n < 0:
        n = abs(n)
        return time_begin - datetime.timedelta(days=n)
    else:
        return time_begin + datetime.timedelta(days=n)


def yuan2cent(value):
    return int(round(value * 100))


def cent2yuan(value):
    val = int(value)
    return float(str(val / 100) + '.' + ('%02d' % (val % 100)))

def randomStr(n=16):
    '''generate a SHORT random string include digits and letters.
    '''
    SAMPLE = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join([random.choice(SAMPLE) for _i in xrange(n)])


"""
编码处理
"""


def unicode2utf8(text):
    if isinstance(text, types.UnicodeType):
        return text.encode('utf-8')
    else:
        return text


def utf82unicode(text):
    if isinstance(text, types.StringType):
        return text.decode('utf-8')
    else:
        return text
