# -*- coding: utf-8 -*-
from flask.views import MethodView
from flask import request
from ..utils.response import error, success, QFRET
from ..dao.dao import get_orders, get_shopdetail, get_delivery, get_orderoperating
from ..dao.dao import get_lastorderoperating, get_orderstats, cal_orderstats
from ..qflogger import log
from .. import app
import datetime


class OrderUpdate(MethodView):
    """
    有订单变更
    """
    def get(self):
        from .. import socketio
        data = request.values
        try:
            sel = int(data.get("sel", 0))
            day = int(data.get("day", 1))
            ex_min = int(data.get("ex_min", 25))
            shex_min = int(data.get("shex_min", 3))
            psex_min = int(data.get("psex_min", 5))
        except Exception, e:
            return error(QFRET.PARAMERR, "参数错误")
        # 获取订单统计
        if day:
            st = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=day-1)
            en = st + datetime.timedelta(days=1)
        else:
            st = None
            en = None
        try:
            if sel:
                stats = get_orderstats(datetime_start=st, datetime_end=en)
            else:
                stats = cal_orderstats(datetime_start=st, datetime_end=en,
                                       extime_min=ex_min, shanghuex_min=shex_min, deliveryex_min=psex_min)
        except Exception, e:
            log.warn("wrong with get_orderstats(%s,%s,%s,%s,%s): %s" % (st, en, ex_min, shex_min, psex_min, e.message))
            stats = {}
        socketio.emit("orderupdate", {"stats": stats})
        log.info("ok!!orderupdate")
        return str(stats)


class AskIfNew(MethodView):
    """
    检查是否有更新
    """
    def get(self):
        lastid = get_lastorderoperating()
        data = {"data": datetime.datetime.now().strftime(app.config["DATETIME_FORMAT"]), "lastid": lastid}
        return success(data=data)


class OrderGet(MethodView):
    """
    获取订单
    """
    def get(self):
        data = request.values
        try:
            rstate = data.get("state", "")
            rordertype = data.get("type", "")
            state = []
            ordertype = []
            if rstate:
                rstate = rstate.split(",")
                for s in rstate:
                    state.append(int(s))
            if rordertype:
                rordertype = rordertype.split(",")
                for o in rordertype:
                    ordertype.append(int(o))
            page = int(data.get("page", 1))
            pagesize = int(data.get("pagesize", 50))
            exp_time_all = int(data.get("exp_time_all", 0))
            exp_time = int(data.get("exp_time", 0))
            day = data.get("day", 1)
            try:
                day = int(day)
                date = 0
            except ValueError:
                date = datetime.datetime.strptime(day, "%Y-%m-%d")
                day = 0
            lastoid = int(data.get("lastoid", 0))
        except Exception, e:
            return error(QFRET.PARAMERR, "参数错误")
        orders = []
        ids = []
        epdura = 25
        epshdura = 3
        eppsdura = 5
        if day:
            st = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=day-1)
            en = st + datetime.timedelta(days=1)
        else:
            st = None
            en = None
            if date:
                st = date
                en = date + datetime.timedelta(days=1)
        for o in get_orders(datetime_start=st, datetime_end=en, page=page, pagesize=pagesize,
                            extime_min=exp_time, extime_min_all=exp_time_all, ordertype=ordertype, state=state):
            o = o.to_dict()
            #期望送达时间
            et = o["pay_time"]+datetime.timedelta(minutes=epdura)
            o["expected_date"] = et.strftime("%Y-%m-%d %H:%M:%S")
            o["lefttime"] = 0
            o["wstatus"] = get_status(o["status"])
            try:
                ushop = get_shopdetail(o["qf_uid"])
                ushop["_id"] = str(ushop["_id"])
                o["shop"] = ushop
            except Exception, e:
                log.warn("cant find shop, qf_u: %s, %s" % (o["qf_uid"], e.message))
            ids.append(str(o["id"]))
            orders.append(o)
        # 获取好近侠配送信息
        order_deliveries = get_delivery(ids)
        if order_deliveries and order_deliveries["respcd"] == '0000':
            order_deliveries = order_deliveries["data"]["orders"]
        else:
            order_deliveries = []
        if len(order_deliveries) != len(orders):
            log.warn("something wrong with order_deliveries! %s:%s" % (len(order_deliveries), len(orders)))
        for o in orders:
            for d in order_deliveries:
                if int(d["orderid"]) == o["id"]:
                    d["wstatus"] = get_deliverystatus(d["status"])
                    o["delivery"] = d
        # 获取订单统计
        try:
            stats = cal_orderstats(datetime_start=st, datetime_end=en,
                                   extime_min=epdura, shanghuex_min=epshdura, deliveryex_min=eppsdura)
        except Exception, e:
            log.warn("wrong with get_orderstats(%s,%s,%s): %s" % (st, en, lastoid, e.message))
            stats = {}

        return success(data={"orders": orders, "stats": stats})


class OrderOperating(MethodView):
    """
    获取订单状态更变记录
    """
    def get(self):
        data = request.values
        try:
            order_id = int(data.get("order_id", ""))
        except Exception, e:
            return error(QFRET.PARAMERR, "参数错误")
        oops = get_orderoperating(order_id=order_id)
        orderops = []
        for o in oops:
            o = o.to_dict()
            o["wtype"] = get_operatingtype(o["operate_type"])
            orderops.append(o)
        return success(data={"ops": orderops})


class DeliveryAnalysis(MethodView):
    """
    获取配送员信息
    """
    def get(self):
        from ..dao.dao import get_delivery_analysis, get_delivery_session
        from flask import session
        sessionname = "delivery_session"
        if sessionname not in session:
            cookies = get_delivery_session()
        else:
            cookies = session[sessionname]
        if "sessionid" in cookies:
            session[sessionname] = cookies
            ana_Data = get_delivery_analysis(cookies)
            return success(data={"analysis": ana_Data})
        else:
            return success(data={"error": "can't get session"})

def get_status(istatus):
    """
    1 待付款
    2 已付款
    3 已确认 (外卖订单确认)
    5 卖家发货
    10 已完成(送达)
    11 系统关闭
    4 已发货（旧版已发货，好近已弃用）
    6 已收货 (未使用)
    7 已评价(未使用)
    8 申请退款
    9 退款订单完成
    *外卖流程：1，2，3，12，5，10
    """
    istatus = int(istatus)
    if istatus == 1:
        return "订单创建"
    elif istatus == 2:
        return "消费者已付款"
    elif istatus == 3:
        return "商家已确认"
    elif istatus == 5:
        return "正在派送中"
    elif istatus == 6:
        return "已收货"
    elif istatus == 7:
        return "已评价"
    elif istatus == 8:
        return "申请退款"
    elif istatus == 9:
        return "退款完成"
    elif istatus == 10:
        return "已送达"
    elif istatus == 11:
        return "系统关闭"
    elif istatus == 12:
        return "配送员已确认"
    elif istatus == 90:
        return "撤销"
    elif istatus == 80:
        return "商户关闭"


def get_operatingtype(istatus):
    """
    订单操作常量类
    """
    if istatus == 0:
        return "订单创建"
    elif istatus == 3:
        return "消费者已付款"
    elif istatus == 17:
        return "商家已确认"
    elif istatus == 19:
        return "配送员已确认"
    elif istatus == 4:
        return "正在派送中"
    elif istatus == 18:
        return "已送达"
    else:
        return istatus


def get_deliverystatus(istatus):
    """
    订单状态常量类
    """
    if istatus == 0:
        return "订单取消"
    elif istatus == 1:
        return "商家已确认"
    elif istatus == 2:
        return "配送员已确认"
    elif istatus == 3:
        return "正在派送中"
    elif istatus == 4:
        return "已送达"
    else:
        return istatus