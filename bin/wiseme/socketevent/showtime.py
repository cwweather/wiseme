# -*- coding: utf-8 -*-
import datetime
import time
import gevent
from flask.ext.socketio import emit
from .. import app
from .. import socketio
from ..qflogger import log
from ..dao.dao import get_lastorderoperating, get_region_list, get_current_puv, get_lastnote, groupby_bi_notes
from ..dao.dao import get_day_pvuv


@socketio.on("askfortime")
def showtime(msg):
    log.info(msg)
    while 1:
        lastid = get_lastorderoperating()
        emit("time", {
            "data": datetime.datetime.now().strftime(app.config["DATETIME_FORMAT"]),
            "lastid": lastid})
        gevent.sleep(1)


@socketio.on("askrlpvuv")
def showpvuv(msg):
    log.info(msg)
    lastid_then = 0
    regions = list(get_region_list())
    region_time_gap = 5
    region_time_count = 0
    t_data = get_day_pvuv(0, 5)
    clock = t_data["clock"]
    while 1:
        today = datetime.datetime.now().date()
        today_start = datetime.datetime(today.year, today.month, today.day)
        now = datetime.datetime.now()
        now_time = now.strftime("%Y-%m-%d %H:%M:%S")
        last = get_lastnote(field={"_id": 1}, sort=[("datetime", -1)])
        if last:
            lastid = last["_id"]
        if lastid == lastid_then:
            #没有新数据就直接跳过
            emit("currentpvuv", {"time": now_time})
            gevent.sleep(1)
            continue
        lastid_then = lastid

        # pvuv
        t_puv = get_current_puv(0, 5)
        y_puv = get_current_puv(1, 5)
        pvuv = {
            "t": t_puv,
            "y": y_puv,
        }

        # 日活
        data = []
        if region_time_count < region_time_gap:
            region_time_count += 1
            for r in regions:
                region_id = str(r["_id"])
                d = len(groupby_bi_notes({
                    "datetime": {"$gt": today_start, "$lt": now},
                    "path": "/locate_circle",
                    "city_region_id": region_id
                }, key={"user_id": 1}))
                data.append({
                    "region_id": region_id,
                    "region": r["name"],
                    "dau": d
                })
        else:
            region_time_count = 0

        index = t_puv["timeblock"]
        clock[index] = {
            "datetime": clock[index]["datetime"],
            "pv": t_puv["cur_pv"],
            "uv": t_puv["cur_uv"]
        }
        emit("currentpvuv", {"time": now_time, "pvuv": pvuv, "dau_list": data, "clock": clock})
        gevent.sleep(1)

