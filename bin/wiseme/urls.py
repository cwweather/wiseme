# -*- coding: utf-8 -*-
from view import Test, Ping
from view.htpage import HtMain
from view.mainpage import Main, DataMain, Logging, Logout, WxLogging
from view.population import Population
from view.lookorder import LookOrder
from api.order import OrderUpdate, OrderGet, OrderOperating, DeliveryAnalysis
from api.pvuv import Pvuv, SetClock, Daily, Monthly
from api.wxapi import VerifyQYUrl, PushMsg

def urlsmap(app):
    # test
    app.add_url_rule('/test', view_func=Test.as_view('test'), methods=['GET'])  # test
    app.add_url_rule('/ping', view_func=Ping.as_view('ping'), methods=['GET'])  # ping
    app.add_url_rule('/ht', view_func=HtMain.as_view('ht'), methods=['GET'])  # heckthon page

    # mainpage
    app.add_url_rule('/', view_func=Main.as_view('main'), methods=['GET'])  # main
    # 数据圈
    app.add_url_rule('/data', view_func=DataMain.as_view('DataMain'), methods=['GET'])  # DataMain
    app.add_url_rule('/pvuv', view_func=Pvuv.as_view('pvuv'), methods=['GET'])  # pvuv
    app.add_url_rule('/setclock', view_func=SetClock.as_view('setclock'), methods=['GET'])  # setclock
    app.add_url_rule('/daily', view_func=Daily.as_view('daily'), methods=['GET'])  # Daily
    app.add_url_rule('/monthly', view_func=Monthly.as_view('monthly'), methods=['GET'])  # monthly
    # logging登陆跳转
    app.add_url_rule('/logging', view_func=Logging.as_view('logging'), methods=['GET'])  # logging
    # 微信登陆跳转
    app.add_url_rule('/wxlogging', view_func=WxLogging.as_view('wxlogging'), methods=['GET'])  # wxlogging
    # 微信验证企业
    app.add_url_rule('/wxverify', view_func=VerifyQYUrl.as_view('wxverify'), methods=['GET', 'POST'])  # wxverify
    # 微信企业号推送
    app.add_url_rule('/pushwxqy', view_func=PushMsg.as_view('pushwxqy'), methods=['GET'])  # pushwxqy
    # 登出
    app.add_url_rule('/logout', view_func=Logout.as_view('LogOut'), methods=['GET'])  # LogOut
    # population
    app.add_url_rule('/all', view_func=Population.as_view('population'), methods=['GET'])  # all
    # lookorder
    app.add_url_rule('/lookorder', view_func=LookOrder.as_view('lookorder'), methods=['GET'])  # lookorder
    # OrderUpdate
    app.add_url_rule('/orderupdate', view_func=OrderUpdate.as_view('orderupdate'), methods=['GET'])  # OrderUpdate
    # 获取配送员信息
    app.add_url_rule('/deliveryana', view_func=DeliveryAnalysis.as_view('deliveryanalysis'), methods=['GET'])  # DeliveryAnalysis
    # orderget
    app.add_url_rule('/orderget', view_func=OrderGet.as_view('orderget'), methods=['GET'])  # orderget
    # orderoperating
    app.add_url_rule('/orderops', view_func=OrderOperating.as_view('orderops'), methods=['GET'])  # orderoperating