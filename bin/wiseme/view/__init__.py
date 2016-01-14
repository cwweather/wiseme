# -*- coding: utf-8 -*-
from flask.views import MethodView
from flask import render_template
import datetime
from flask import session
from ..utils.response import error, success, QFRET
from ..dao.dao import get_region_list, groupby_bi_notes


class Test(MethodView):
    """
    test
    """
    def get(self):
        data = str(session)
        now = datetime.datetime.now()
        start_time = datetime.datetime(now.year, now.month, now.day)
        regions = list(get_region_list())
        data = []
        for r in regions:
            region_id = str(r["_id"])
            d = len(groupby_bi_notes({
                "datetime": {"$gt": start_time, "$lt": now},
                "path": "/locate_circle",
                "city_region_id": region_id
            }, key={"user_id":1}))
            data.append({
                "region_id": region_id,
                "region": r["name"],
                "dau": d
            })
        return success(data=data)


class Ping(MethodView):
    """
    ping
    """
    def get(self):
        return "OK"
