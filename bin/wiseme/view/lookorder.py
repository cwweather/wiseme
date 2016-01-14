# -*- coding: utf-8 -*-
from flask.views import MethodView
from flask import render_template, request, session
from ..utils.logincheck import check_login


class LookOrder(MethodView):
    """
    订单监控
    """
    @check_login
    def get(self):
        profile = self.qf_u
        return render_template("lookorder.html", profile=profile)