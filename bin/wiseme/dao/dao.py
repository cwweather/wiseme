# -*- coding: utf-8 -*-
import json
import datetime
import pymongo
import psycopg2
from .. import app
from ..qflogger import log
from mysqlmodels import HJFPopulation
from mmwdmodels import Order, OrderOperating
from sqlalchemy import func
from ..utils.qfthrift.thrift_tools import thrift_callex
from ..utils.qfthrift.open_user import OpenUser


def get_population():
    session = app.mysqldb()
    try:
        data = session.query(HJFPopulation).all()
    except:
        data = []
    finally:
        session.close()
    return data


def get_orders(datetime_start=None, datetime_end=datetime.datetime.now(), page=1, pagesize=50,
               extime_min_all=0, extime_min=0, ordertype=None, state=None):
    log.info("get_orders:st%s, en%s, page%s, pagesize%s, ordertype%s, state%s" %
             (datetime_start, datetime_end, page, pagesize, ordertype, state))
    session = app.mmwddb()
    try:
        q = session.query(Order)
        if datetime_start and datetime_end:
            q = q.filter(Order.create_time.between(datetime_start, datetime_end))
        if ordertype and isinstance(ordertype, list):
            q = q.filter(Order.order_type.in_(ordertype))
        if state and isinstance(state, list):
            q = q.filter(Order.status.in_(state))
        if extime_min_all:
            now = datetime.datetime.now()
            q = q.filter(Order.pay_time < now - datetime.timedelta(minutes=extime_min))
        if extime_min:
            now = datetime.datetime.now()
            q = q.filter(Order.update_time < now - datetime.timedelta(minutes=extime_min))
        data = q.order_by(Order.id.desc()).offset((page-1)*pagesize).limit(pagesize).all()
    except Exception, e:
        log.warn(e.message)
        data = []
    finally:
        session.close()
    return data


def cal_orderstats(datetime_start=None, datetime_end=datetime.datetime.now(), extime_min=25, shanghuex_min=3, deliveryex_min=5):
    now = datetime.datetime.now()
    extime = now - datetime.timedelta(minutes=extime_min)
    shanghu_extime = now - datetime.timedelta(minutes=shanghuex_min)
    delivery_extime = now - datetime.timedelta(minutes=deliveryex_min)
    session = app.mmwddb()
    try:
        q = session.query(Order.id, Order.update_time, Order.pay_time, Order.status).filter(Order.order_type == 6)
        if datetime_start and datetime_end:
            q = q.filter(Order.pay_time.between(datetime_start, datetime_end))
        orders = q.order_by(Order.id.desc()).limit(10000).all()
    except Exception, e:
        log.warn(e.message)
        orders = []
    finally:
        session.close()
    oos = 0
    oop = 0
    o1 = 0
    oo1 = 0
    o2 = 0
    oo2 = 0
    o3 = 0
    oo3 = 0
    o4 = 0
    oo4 = 0
    o5 = 0
    oo5 = 0
    for o in orders:
        if o.status == 2:
            o1 += 1
            if o.update_time < shanghu_extime:
                oos += 1
            if o.pay_time < extime:
                oo1 += 1
        elif o.status == 3:
            o2 += 1
            if o.update_time < delivery_extime:
                oop += 1
            if o.pay_time < extime:
                oo2 += 1
        elif o.status == 12:
            o3 += 1
            if o.pay_time < extime:
                oo3 += 1
        elif o.status == 5:
            o4 += 1
            if o.pay_time < extime:
                oo4 += 1
        elif o.status == 10:
            o5 += 1
            if o.pay_time - o.update_time > datetime.timedelta(minutes=extime_min):
                oo5 += 1
    t = datetime.datetime.now()-now
    data = {
            "oos": oos, "oop": oop,
            "o1": o1, "oo1": oo1,
            "o2": o2, "oo2": oo2,
            "o3": o3, "oo3": oo3,
            "o4": o4, "oo4": oo4,
            "o5": o5, "oo5": oo5,
            "t": str(t)
        }
    return data


def get_orderstats(datetime_start=None, datetime_end=datetime.datetime.now(), lastid=0):
    session = app.mmwddb()
    try:
        q = session.query(Order.id, Order.update_time, Order.pay_time, Order.status).filter(Order.order_type == 6)
        if datetime_start and datetime_end:
            q = q.filter(Order.pay_time.between(datetime_start, datetime_end))
        if lastid:
            q = q.filter(Order.id > lastid)
        orders = q.order_by(Order.id.desc()).limit(10000).all()
    except Exception, e:
        log.warn(e.message)
        orders = []
    finally:
        session.close()
    data = {"os": orders}
    return data


def get_orderoperating(order_id=0, page=1, pagesize=50, ifcount=0):
    session = app.mmwddb()
    try:
        if ifcount:
            q = session.query(func.count(OrderOperating.id))
        else:
            q = session.query(OrderOperating)
        if order_id:
            q = q.filter(OrderOperating.order_id==order_id)
        data = q.offset((page-1)*pagesize).limit(pagesize).all()
    except Exception, e:
        data = []
    finally:
        session.close()
    return data


def get_lastorderoperating():
    session = app.mmwddb()
    try:
        data = session.query(OrderOperating.id).order_by(OrderOperating.id.desc()).first()
    except Exception, e:
        data = []
    finally:
        session.close()
    return data


def get_shopdetail(qf_uid=None):
    if qf_uid:
        near = app.mongodb.near
        shop = near.shop.find({"qf_uid": qf_uid})[0]
        shop["_id"] = str(shop["_id"])
        return shop


def get_wisemeuser(unionid, count=1):
    db = app.mongodb.bi
    user = db.wiseuser.find({"unionid": unionid, "main": 1})
    if count:
        return user.count()
    else:
        if user:
            return user[0]
        else:
            return None


def get_delivery(order_ids):
    log.info("get_delivery: order_ids %s" % order_ids)
    handler = app.deliveryhandler
    try:

        order_deliveries = handler.query(order_ids)
    except Exception, e:
        log.warn("get_delivery: %s" % e.message)
        return []
    if order_deliveries and order_deliveries["respcd"] != '0000':
        return []
    return order_deliveries


def get_delivery_session():
    handler = app.deliveryhandler
    try:
        cookies = handler.get_sessionid()
    except Exception, e:
        log.warn("get_sessionid: %s" % e.message)
        return []
    return cookies


def get_delivery_analysis(cookies):
    handler = app.deliveryhandler
    try:
        data = handler.get_analysis(cookies)
    except Exception, e:
        log.warn("get_analysis: %s" % e.message)
        return []
    return data


def get_userinfo(unionid="", user_id=""):
    try:
        OPENUSER_SERVER = app.config["OPENUSER_SERVER"]
        if user_id:
            spec = {'user_id': user_id}
        elif unionid:
            spec = {'unionid': unionid}
        else:
            return {}
        json_spec = json.dumps(spec)
        user = thrift_callex(OPENUSER_SERVER, OpenUser, "get_profiles", app_id=10003, spec=json_spec)
    except Exception, e:
        user = [{}]
    return user[0]


QUERY = {
    "$and":[
        {"user_id": {"$ne": "null"}},
        {"$or": [
            {"path": {"$nin": [
                "/topic", "/android_bind", "/ios_bind",
                "/wp_bind", "/server/qiniu_token", "/", "/get_addr_list", "/get_building_list", "/app_config"]}},
            {"path": "/topic", "method": "POST"}
        ]}
    ]
}

FIELD = {
    "_id": 0,
    "datetime": 1,
    "user_id": 1,
    "path": 1,
    "method": 1,
    "remote_ip": 1,
    "UA": 1,
    "respcd": 1,
    "status": 1,
    "args": 1,
    "host": 1,
    "duration": 1,
}


def get_bi_notes(query={}, field=FIELD, sort=[("datetime", -1)], base_query=QUERY):
    query.update(base_query)
    db = app.mongodb.bi
    newact = db.note.find(query, field, sort=sort)
    return newact


def get_buy_actions(date_from="", date_end=""):
    now = datetime.datetime.now()
    if not date_from:
        date_from = datetime.datetime(now.year, now.month, now.day)
    if not date_end:
        date_end = now
    q = {
        "datetime": {"$gt": date_from, "$lt": date_end},
        "path": {"in": [
            "/api/order/take_out_buy",
            "/api/order/special_sale_buy",
            "/api/order/paybill",
            "/api/order/activity_buy",
            "/api/order/cdc_pay"
        ]}
    }
    buylog = get_bi_notes(q)
    buylinks = []
    for bl in buylog:
        link = {
            "source": bl["user_id"],
            "username": "C",
            "img": "",
            "datetime": bl["datetime"].strftime('%Y-%m-%d %H:%M:%S'),
            "type": "a",
            "dist": 1,
            "shopname": "B"
        }
        order_id = bl["ret"]["data"]["order_id"]
        #TODO: 根据order_id 从orders表里获取 qf_uid
        #TODO: 验证订单有效性
        link["target"] = int(order_id)
        user_id = bl["user_id"]
        #TODO: 根据user_id 获取头像，昵称
        #link["username"] = user_data
        #link["img"] = user_data
        buylinks.append(link)
    return buylinks


def get_lastnote(query={}, field=FIELD, sort=[("datetime", -1)], base_query=QUERY):
    query.update(base_query)
    db = app.mongodb.bi
    newact = db.note.find_one(query, field, sort=sort)
    return newact


def groupby_bi_notes(query={}, key={"path": 1}, base_query=QUERY):
    query.update(base_query)
    db = app.mongodb.bi
    path_count = db.note.group(
        key=key,
        condition=query,
        initial={"count": 0}, reduce="function(obj, prev){prev.count++;}"
    )
    return path_count


def get_region_list():
    db = app.mongodb.near
    regions = db.region.find({"status": 1})
    return regions


def get_allday_temai(days_before_today=0):
    last_day = days_before_today
    now = datetime.datetime.now()
    start_time = datetime.datetime(now.year, now.month, now.day)
    if last_day:
        start_time = start_time - datetime.timedelta(days=last_day)
        now = start_time + datetime.timedelta(days=1)
    buy_q = {"datetime": {"$gt": start_time, "$lt": now}, "path": "/api/order/buy"}
    cdc_q = {"datetime": {"$gt": start_time, "$lt": now}, "path": "/api/order/cdc_pay"}
    abuy_q = {"datetime": {"$gt": start_time, "$lt": now}, "path": "/api/order/activity_buy"}
    paid_q = {"datetime": {"$gt": start_time, "$lt": now}, "path": "/api/order/qtpay_ispayed"}
    bpaid_q = {"datetime": {"$gt": start_time, "$lt": now}, "path": "/api/order/qtpay_ispayed", "respcd": {"$ne": "0000"}}
    all_buy = get_bi_notes(buy_q).count()
    all_cdc = get_bi_notes(cdc_q).count()
    all_abuy = get_bi_notes(abuy_q).count()
    all_paid = get_bi_notes(paid_q).count()
    all_bpaid = get_bi_notes(bpaid_q).count()
    return {"allbuy": all_buy, "allcdc": all_cdc, "allabuy": all_abuy, "allpaid": all_paid, "allbpaid": all_bpaid}


def set_buyaction(date_from="", date_end=""):
    now = datetime.datetime.now()
    if not date_from:
        date_from = datetime.datetime(now.year, now.month, now.day)
    if not date_end:
        date_end = now
    # 取提前10分钟的订单反正数据遗漏
    orders = get_orders(date_from - datetime.timedelta(minutes=10), date_end, pagesize=5000,
                        ordertype=[4, 5, 6], state=[2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 80, 90])
    q = {
        "datetime": {"$gt": date_from, "$lt": date_end},
        "path": {"in": [
            "/api/order/take_out_buy",
            "/api/order/special_sale_buy",
            "/api/order/paybill",
            "/api/order/activity_buy",
            "/api/order/cdc_pay"
        ]}
    }
    buylog = get_bi_notes(q)
    buylinks = []
    db = app.mongodb_for_write.bi
    for bl in buylog:
        link = {
            "source": bl["user_id"],
            "username": "C",
            "img": "",
            "datetime": bl["datetime"].strftime('%Y-%m-%d %H:%M:%S'),
            "type": "a",
            "dist": 1,
            "shopname": "B"
        }
        order_id = bl["ret"]["data"]["order_id"]
        #TODO: 根据order_id 从orders表里获取 qf_uid
        for o in orders:
            o = o.to_dict()
            if order_id == o["id"]:
                link["target"] = int(o["qf_uid"])
                break
        #TODO: 验证订单有效性
        link["target"] = int(order_id)
        user_id = bl["user_id"]
        #TODO: 根据user_id 获取头像，昵称
        #link["username"] = user_data
        #link["img"] = user_data
        buylinks.append(link)
        db.buyactions.insert_one(link)


def set_clock(req_time=None, gap=5):
    if not req_time:
        req_time = datetime.datetime.now()
    thedaystart = datetime.datetime(req_time.year, req_time.month, req_time.day)
    req_time_minu = (req_time - thedaystart).seconds/(gap*60)  # 取整
    start_time = thedaystart + datetime.timedelta(minutes=(gap*(req_time_minu-1)))
    end_time = thedaystart + datetime.timedelta(minutes=(gap*req_time_minu))
    # 检查库中是否已经存在
    db = app.mongodb_for_write.bi
    checkexist = db.clock.find({"enddate": end_time, "gap": gap})
    if checkexist.count():
        return {"data": {
                    "enddate": checkexist[0].enddate,
                    "gap": checkexist[0].gap,
                    "pv": checkexist[0].pv,
                    "uv": checkexist[0].uv
                }, "result": checkexist[0]._id}
    query = {"datetime": {"$gt": start_time, "$lte": end_time}}
    pv = get_bi_notes(query).count()
    uv = len(groupby_bi_notes(query, {"user_id": 1}))
    newact = {
        "enddate": end_time,
        "gap": gap,
        "pv": pv,
        "uv": uv
    }
    result = db.clock.insert_one(newact)
    if result.inserted_id:
        return {"data": newact, "result": result}
    return {"data": "", "result": result}


def get_clock(start_date, end_date, gap=5):
    db = app.mongodb.bi
    clockblocks = db.clock.find({
        "enddate": {"$gt": start_date, "$lte": end_date},
        "gap": gap
    }).sort("enddate", pymongo.ASCENDING)
    return clockblocks


def get_day_pvuv(days_before_today=0, gap=5):
    """
    获取今天各时间区间格内的pv和uv
    :param days_before_today:
    :param gap: minutes
    :return:
    """
    # 初始化时间
    last_day = days_before_today
    now = datetime.datetime.now()
    start_time = datetime.datetime(now.year, now.month, now.day)
    if last_day:
        start_time = start_time - datetime.timedelta(days=last_day)
        now = start_time + datetime.timedelta(days=1)
    # 获取当日的数据时间格
    clockblocks = list(get_clock(start_time, now))
    clockcount = len(clockblocks)

    # 根据数据格填充pvuv
    clock_list = []
    iblock = 0
    all_pv = 0
    all_uv = 0
    for minu in range(1, 24*60/gap+1):
        date = start_time + datetime.timedelta(minutes=gap*minu)
        if date > now:
            clock_list.append({
                "datetime": date.strftime("%Y-%m-%d %H:%M:00"),
                "pv": 0,
                "uv": 0
            })
            continue
        # 检查数据格是否存在，不存在则将添加新数据格
        if iblock >= clockcount:
            dateinblock = ""
        else:
            dateinblock = clockblocks[iblock]["enddate"]
        log.info("========")
        log.info("iblock=%s;clockcount=%s" % (str(iblock), clockcount))
        log.info("dateinblock=%s" % str(dateinblock))
        if date != dateinblock:
            block = set_clock(date, gap)["data"]
        else:
            block = clockblocks[iblock]
            iblock += 1
        log.info("block:%s" % block)
        log.info("========")
        data = {
            "datetime": date.strftime("%Y-%m-%d %H:%M:00"),
            "pv": block["pv"],
            "uv": block["uv"]
        }
        all_pv += block["pv"]
        all_uv += block["uv"]
        clock_list.append(data)
    return {"all_pv": all_pv, "all_uv": all_uv, "clock": clock_list}


def get_current_puv(days_before_today=0, gap=5, pv=1, uv=1):
    req_time = datetime.datetime.now()
    #today仅表示查询时间当日的00:00:00，当days_before_today＝1时表示昨日00:00:00
    today = datetime.datetime(req_time.year, req_time.month, req_time.day)
    if days_before_today:
        req_time = req_time - datetime.timedelta(days=days_before_today)
        today = today - datetime.timedelta(days=days_before_today)
    req_time_minu = (req_time - today).seconds/(60 * gap)
    start_time = today + datetime.timedelta(minutes=(gap*req_time_minu))
    p_count = 0
    u_count = 0
    if pv:
        p_count = get_bi_notes({"datetime": {"$gt": start_time, "$lt": req_time}}).count()
    if uv:
        u_count = len(groupby_bi_notes({"datetime": {"$gt": start_time, "$lt": req_time}}, {"user_id": 1}))
    timegap = start_time + datetime.timedelta(minutes=gap)
    data = {
        "time": timegap.strftime("%Y-%m-%d %H:%M:00"),
        "timeblock": req_time_minu
    }
    if uv:
        data.update({"cur_uv": u_count})
    if pv:
        data.update({"cur_pv": p_count})
    return data


def get_daily_data(date, service_region_id=None, province=None, city=None, county=None):
    cur = app.psql.connect()
    cur.execute("select * from f_busiregion where c_yearmonthday='%s' order by service_region_id" % date)
    rows = cur.fetchall()
    cur.close()
    data = []
    last = {}
    i = -1
    for r in rows:
        # 创建商圈类
        if not last or last[9] != r[9]:
            i += 1
            data.append({
                "region_id": r[9],
                "region": r[10],
                "yearmonthday": r[1],
                "product_code": r[4],
                "province_name": r[6],
                "city_name": r[7],
                "county_name": r[8]
            })
            last = r
        data[i].update({
            r[11]: {"name": r[12], "value": r[13]}
        })
    return data


def get_daily_text(date):
    data = get_daily_data(date)
    text = date + "\n\n"
    for d in data:
        t = ""
        t += (d["region"] + "\n")
        if "y_tm_amt" in d:
            cmt = str((d["y_tm_amt"]["value"])/100)
            t += ("特卖:" + cmt + "元/" + str(d["y_tm_cnt"]["value"]) + "笔 \n")
        if "y_wm_amt" in d:
            cmt = str((d["y_wm_amt"]["value"])/100)
            t += ("外卖:" + cmt + "元/" + str(d["y_wm_cnt"]["value"]) + "笔 \n")
        if "y_md_amt" in d:
            cmt = str((d["y_md_amt"]["value"])/100)
            t += ("买单:" + cmt + "元/" + str(d["y_md_cnt"]["value"]) + "笔 \n")
        if "y_tm_amt" in d and "y_wm_amt" in d and "y_md_amt" in d and "y_tm_cnt" in d and "y_wm_cnt" in d and "y_md_cnt" in d:
            cmt = str((d["y_tm_amt"]["value"]+d["y_wm_amt"]["value"]+d["y_md_amt"]["value"])/100)
            cnt = str(d["y_tm_cnt"]["value"]+d["y_wm_cnt"]["value"]+d["y_md_cnt"]["value"])
            t += ("总:" + cmt + "元/" + cnt + "笔\n")
        if "y_dau" in d:
            dau = str((d["y_dau"]["value"]))
            t += ("日活用户数:" + dau + " \n")
        if "y_user_add_cnt" in d:
            dau = str((d["y_user_add_cnt"]["value"]))
            t += ("新增用户数:" + dau + " \n")
        if "user_cnt" in d:
            dau = str((d["user_cnt"]["value"]))
            t += ("累计用户数:" + dau + " \n")
        if "y_trade_hjuser_cnt" in d:
            dau = str((d["y_trade_hjuser_cnt"]["value"]))
            t += ("交易用户数:" + dau + " \n")
        if "y_wx_num" in d and "y_wx_amt" in d:
            cmt = str((d["y_wx_amt"]["value"])/100)
            t += ("微信支付:" + cmt + "元/" + str(d["y_wx_num"]["value"]) + "笔 \n")
        if "y_sale_shop_cnt" in d:
            y_sale_shop_cnt = str((d["y_sale_shop_cnt"]["value"]))
            t += ("微信交易商户数:" + y_sale_shop_cnt + " \n")
        text += "\n"
        text += t
    return text


def get_today_text():
    now = datetime.datetime.now()
    today_start = datetime.datetime(now.year, now.month, now.day)
    text = "今天是" + now.strftime("%Y-%m-%d") + "周" + str(now.weekday()) + "\n\n"
    regions = list(get_region_list())
    for r in regions:
        region_id = str(r["_id"])
        d = len(groupby_bi_notes({
            "datetime": {"$gt": today_start, "$lt": now},
            "path": "/locate_circle",
            "city_region_id": region_id
        }, key={"user_id": 1}))

        t = ""
        t += (r["name"] + " 今日日活:" + str(d) + "\n")
        text += t
    return text


def get_month_data(date_from, date_end):
    cur = app.psql.connect()
    day_gap = (date_end - date_from).days
    date_list = []
    region_list = set([])
    for i in range(0, day_gap):
        date = (date_from + datetime.timedelta(days=i)).strftime("%Y-%m-%d")
        cur.execute("select * from f_busiregion where c_yearmonthday='%s' order by c_yearmonthday, service_region_id" % date)
        rows = cur.fetchall()
        region_data = {}
        # 日数据整理
        last = ""
        i = -1
        for r in rows:
            # 创建商圈类
            if not last or last != r[9]:
                i += 1
                region_list.add(r[10])
                region_data.update({
                    r[10]: {
                        "region_id": r[9],
                        "yearmonthday": r[1],
                        "product_code": r[4],
                        "province_name": r[6],
                        "city_name": r[7],
                        "county_name": r[8]
                    }
                })
                last = r[9]

            region_data[r[10]].update({
                r[11]: r[13]
            })
        date_list.append({"date": date, "regions": region_data})
    cur.close()
    return {"data": date_list, "region_list": list(region_list)}
