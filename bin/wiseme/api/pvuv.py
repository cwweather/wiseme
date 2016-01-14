# -*- coding: utf-8 -*-
from flask.views import MethodView
from flask import request
from ..utils.response import error, success, QFRET
from ..dao.dao import get_day_pvuv, get_current_puv, get_allday_temai, set_clock, get_daily_data, get_month_data
from ..qflogger import log
from .. import app
import datetime


class SetClock(MethodView):
    """
    设置缓存时钟中的数据
    """
    def get(self):
        ret = set_clock()
        return success({"data": str(ret["data"])})


class Pvuv(MethodView):
    """
    pvuv数据
    """
    def get(self):
        y_data = get_day_pvuv(1, 5)
        t_data = get_day_pvuv(0, 5)
        return success({"y": y_data, "t": t_data})


class Daily(MethodView):
    """
    好近日报数据
    """
    def get(self):
        param = request.values
        try:
            date = param.get("date", "")
        except Exception, e:
            return error(QFRET.PARAMERR, "参数错误")
        if not date:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        ret = get_daily_data(date)
        return success(ret)


class Monthly(MethodView):
    """
    一个月的报表信息
    """
    def get(self):
        param = request.values
        try:
            days = param.get("days", 30)
        except Exception, e:
            return error(QFRET.PARAMERR, "参数错误")
        date_end = datetime.datetime.now()
        date_from = date_end - datetime.timedelta(days=days)
        ret = get_month_data(date_from, date_end)
        return success(ret)