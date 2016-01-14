# -*- coding: utf-8 -*-
from flask.views import MethodView
from flask import render_template
from ..dao.dao import get_population
from ..utils.logincheck import check_login
import datetime

class Population(MethodView):
    """
    main
    """
    @check_login
    def get(self):
        pop = get_population()
        ret_pop = []
        for p in pop:
            ret_p = p.to_dict()
            ret_p["weekday"] = datetime.datetime.strptime(ret_p["c_yearmonthday"], "%Y-%m-%d").weekday()
            ret_p["others_amt"] = float(ret_p["wx_amt"])-float(ret_p["tm_amt"])-float(ret_p["zx_amt"])
            ret_p["others_num"] = float(ret_p["wx_num"])-float(ret_p["tm_num"])-float(ret_p["zx_num"])
            ret_pop.append(ret_p)
        return render_template("daily.html", profile=self.qf_u, population=ret_pop)