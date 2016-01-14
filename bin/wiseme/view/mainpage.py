# -*- coding: utf-8 -*-
from flask.views import MethodView
from flask import render_template, request, session, redirect
from ..utils.logincheck import get_access_token, check_login
from ..utils.response import error, QFRET
from ..utils.logincheck import logout
from ..qflogger import log
from .. import app
from ..dao.dao import get_wisemeuser


class Main(MethodView):
    """
    main
    """
    @check_login
    def get(self):
        data = request.values
        profile = self.qf_u
        return render_template("main.html", profile=profile)


class DataMain(MethodView):
    """
    数据圈
    """
    @check_login
    def get(self):
        profile = self.qf_u
        return render_template("datamain.html", profile=profile)


class Logging(MethodView):
    """
    验证登陆跳转
    """
    def get(self):
        data = request.values
        url = data.get("state", "")
        wx_code = data.get("code", "")
        access_data = get_access_token(wx_code)
        if "errcode" in access_data:
            msg = str(access_data["errcode"])+access_data["errmsg"]
            return error(QFRET.SESSIONERR, respmsg=msg, escape=False)
        if "unionid" not in access_data:
            return redirect(location="")
        unionid = access_data["unionid"]
        # 保存unionid
        log.info("unionid: %s" % unionid)
        session["unionid"] = unionid
        return redirect(location=url)


class WxLogging(MethodView):
    """
    微信登陆跳转
    """
    def get(self):
        data = request.values
        url = data.get("state", "")
        wx_code = data.get("code", "")
        access_data = get_access_token(wx_code, 1)
        if "errcode" in access_data:
            msg = str(access_data["errcode"])+access_data["errmsg"]
            return error(QFRET.SESSIONERR, respmsg=msg, escape=False)
        if "unionid" not in access_data:
            return redirect(location="")
        unionid = access_data["unionid"]
        # 保存unionid
        log.info("unionid: %s" % unionid)
        session["unionid"] = unionid
        return redirect(location=url)


class Logout(MethodView):
    """
    登出
    """
    def get(self):
        logout()
        return render_template("main.html", openid="welcome!")