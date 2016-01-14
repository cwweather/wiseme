# -*- coding: utf-8 -*-
from flask import request, session, render_template
from .. import app
from response import error, QFRET
from urllib import urlopen
from ..dao.dao import get_wisemeuser, get_userinfo
from ..qflogger import log
import json


def check_login(func):
    """
    登陆检查
    """
    def _(self, *args, **kwargs):
        if app.config["DEBUG"]:
            qf_u = {
                "uid": "36",
                "nickname": "qfpay测试",
                "avatar": "http://wx.qlogo.cn/mmopen/r48cSSlr7jgWic0R1PvfDYFwFV0XicXIh2SKuzKpnwxKeNw3JZh6YEbrPkz55W2EPklgpnMmAa5icZmJYCgOnrt6tJhmRZ9R9XL\\0"
            }
            qf_u["nickname"] = qf_u["nickname"].decode("utf-8")
            self.qf_u = qf_u
            session["qf_u"] = qf_u
            #oZCS6s5DvT_PdszpDkZatIExRp_E
            return func(self, *args, **kwargs)
        if "unionid" not in session:
            wxappid = app.config["WX_APPID"]
            wxappdomain = app.config["WX_CALLBACK_DOMAIN"]
            redirect_url = request.full_path[:-1]
            if redirect_url == "/":
                redirect_url = ""
            return render_template("qrlogin.html", wxappid=wxappid, domain=wxappdomain, redirect=redirect_url, state="/")
        else:
            unionid = session["unionid"]
        checkuser = get_wisemeuser(unionid)
        if not checkuser:
            del(session["unionid"])
            log.info("not authorized unionid: %s" % unionid)
            return render_template("error.html", respmsg="用户未经授权，请在蜂巢中授权")
        else:
            if "qf_u" not in session:
                try:
                    qfprofile = get_userinfo(unionid)
                    qf_u = {
                        "uid": qfprofile.user_id,
                        "nickname": qfprofile.nickname.decode("utf-8"),
                        "avatar": qfprofile.avatar
                    }
                    session["qf_u"] = qf_u
                except Exception, e:
                    log.warn(e.message)
                    return render_template("error.html", respmsg="获取用户详情错误！请联系开发人员")
            else:
                try:
                    qf_u = {
                        "uid": session["qf_u"]["uid"],
                        "nickname": session["qf_u"]["nickname"],
                        "avatar": session["qf_u"]["avatar"]
                    }
                except Exception, e:
                    log.warn(e.message)
                    return render_template("error.html", respmsg="数据出错，请重新登录")
            self.qf_u = qf_u
            return func(self, *args, **kwargs)
    return _


def logout():
    """
    登出
    """
    try:
        if "unionid" in session:
            del(session["unionid"])
    except Exception, e:
        log.warn(e.message)
        return False
    return True


def wx_access(func):
    """
    获取微信信息
    """
    def _(self, *args, **kwargs):
        try:
            redirect_url = request.values.get("redirect_url", "http%3A%2F%2Fdata.haojin.in")
            unionid = session["unionid"]
        except Exception, e:
            return render_template("qrlogin.html", redirect=redirect_url)
        db = app.mongodb.bi
        if db.wisemeuser.find({"unionid": unionid, "main": 1}).count():
            return func(self, *args, **kwargs)
        else:
            return error(QFRET.SESSIONERR, respmsg="用户未经授权，请在蜂巢中授权", escape=False)
    return _


def get_access_token(wx_code, appflag=0):
    """
    获取accesstoken
    :param wx_code:
    :param app: 0使用WX_APPID 1使用QF_APPID
    :return:
    """
    if not wx_code:
        return ""
    if appflag:
        wx_appid = app.config["QF_APPID"]
        wx_appsecret = app.config["QF_APPSECRET"]
    else:
        wx_appid = app.config["WX_APPID"]
        wx_appsecret = app.config["WX_APPSECRET"]
    url = "https://api.weixin.qq.com/sns/oauth2/access_token?appid={}&secret={}&code={}&grant_type=authorization_code".format(
        wx_appid, wx_appsecret, wx_code)
    wx_req = urlopen(url)
    wx_data = wx_req.read()
    json_str = ""
    if wx_data:
        try:
            json_str = json.loads(wx_data)
        except Exception, e:
            return "解析错误: %s" % json_str
    return json_str