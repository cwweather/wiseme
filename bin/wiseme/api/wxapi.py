# -*- coding: utf-8 -*-
from flask.views import MethodView
from flask import request
from ..utils.response import error, success, QFRET
from ..utils.WXBizMsgCrypt import WXBizMsgCrypt
from ..qflogger import log
from .. import app
from ..dao.dao import get_daily_text, get_today_text
from urllib import urlopen, urlencode
import urllib2
import xml.etree.cElementTree as ET
import datetime
import json


class VerifyQYUrl(MethodView):

    def get(self):
        """
        验证企业url
        :return:
        """
        param = request.values
        try:
            msg_signature = param.get("msg_signature")
            timestamp = param.get("timestamp")
            nonce = param.get("nonce")
            echostr = param.get("echostr")
        except Exception, e:
            return error(QFRET.PARAMERR, "参数错误")
        if not msg_signature or not timestamp or not nonce or not echostr:
            return error(QFRET.PARAMERR, "参数错误")

        wxcpt = WXBizMsgCrypt(app.config["WX_TOKEN"], app.config["WX_AESKEY"], app.config["QY_APPID"])
        ret, sEchoStr = wxcpt.VerifyURL(msg_signature, timestamp, nonce, echostr)
        if ret != 0:
            log.warn("ERR: VerifyURL ret: " + str(ret))
            return "ERR: VerifyURL ret: " + str(ret)
        else:
            log.info("ret:%s echostr:%s" % (ret, sEchoStr))
            return sEchoStr

    def post(self):
        """
        接受企业号请求
        :return:
        """
        def event_menu_click(eventkey, date=""):
            if eventkey == "DAILY_Y":
                #昨日日报请求
                date = (datetime.datetime.now()-datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                text = get_daily_text(date)
                sRespData = "<xml>" \
                          "<ToUserName><![CDATA[%s]]></ToUserName>" \
                          "<FromUserName><![CDATA[%s]]></FromUserName>" \
                          "<CreateTime>%s</CreateTime>" \
                          "<MsgType><![CDATA[text]]></MsgType>" \
                          "<Content><![CDATA[%s]]></Content>" \
                          "</xml>" % (
                    fromuser,
                    touser,
                    timestamp,
                    text
                )
                log.info("wx req key: %s data: %s" %(eventkey, sRespData))
                ret, sEncryptMsg = wxcpt.EncryptMsg(sRespData.encode("utf-8"), nonce, timestamp)
                if ret == 0:
                    return sEncryptMsg
                else:
                    log.warn("ERR: EncryptMsg ret: " + str(ret))
                    return ""
            elif eventkey == "DAILY_T":
                # 日活
                text = get_today_text()
                sRespData = "<xml>" \
                          "<ToUserName><![CDATA[%s]]></ToUserName>" \
                          "<FromUserName><![CDATA[%s]]></FromUserName>" \
                          "<CreateTime>%s</CreateTime>" \
                          "<MsgType><![CDATA[text]]></MsgType>" \
                          "<Content><![CDATA[%s]]></Content>" \
                          "</xml>" % (
                    fromuser,
                    touser,
                    timestamp,
                    text
                )
                log.info("wx req key: %s data: %s" %(eventkey, sRespData))
                ret, sEncryptMsg = wxcpt.EncryptMsg(sRespData.encode("utf-8"), nonce, timestamp)
                if ret == 0:
                    return sEncryptMsg
                else:
                    log.warn("ERR: EncryptMsg ret: " + str(ret))
                    return ""
            elif eventkey == "DAILY_HISTORY":
                text = get_daily_text(date)
                sRespData = "<xml>" \
                          "<ToUserName><![CDATA[%s]]></ToUserName>" \
                          "<FromUserName><![CDATA[%s]]></FromUserName>" \
                          "<CreateTime>%s</CreateTime>" \
                          "<MsgType><![CDATA[text]]></MsgType>" \
                          "<Content><![CDATA[%s]]></Content>" \
                          "</xml>" % (
                    fromuser,
                    touser,
                    timestamp,
                    text
                )
                log.info("wx req key: %s data: %s" %(eventkey, sRespData))
                ret, sEncryptMsg = wxcpt.EncryptMsg(sRespData.encode("utf-8"), nonce, timestamp)
                if ret == 0:
                    return sEncryptMsg
                else:
                    log.warn("ERR: EncryptMsg ret: " + str(ret))
                    return ""
            else:
                #未知请求返回帮助
                sRespData = "<xml>" \
                          "<ToUserName><![CDATA[%s]]></ToUserName>" \
                          "<FromUserName><![CDATA[%s]]></FromUserName>" \
                          "<CreateTime>%s</CreateTime>" \
                          "<MsgType><![CDATA[text]]></MsgType>" \
                          "<Content><![CDATA[%s]]></Content>" \
                          "</xml>" % (
                    fromuser,
                    app.config["QY_APPID"],
                    timestamp,
                    "欢迎使用钱方好近数据圈！查看详情请登陆数据圈"
                )
                log.info("wx req key: %s data: %s" %(eventkey, sRespData))
                ret, sEncryptMsg = wxcpt.EncryptMsg(sRespData.encode("utf-8"), nonce, timestamp)
                if ret == 0:
                    return sEncryptMsg
                else:
                    log.warn("ERR: EncryptMsg ret: " + str(ret))
                    return ""
        param = request.values
        try:
            msg_signature = param.get("msg_signature")
            timestamp = param.get("timestamp")
            nonce = param.get("nonce")
            reqdata = request.data
        except Exception, e:
            return error(QFRET.PARAMERR, "参数错误")
        if not msg_signature or not timestamp or not nonce or not reqdata:
            return error(QFRET.PARAMERR, "参数错误")
        wxcpt = WXBizMsgCrypt(app.config["WX_TOKEN"], app.config["WX_AESKEY"], app.config["QY_APPID"])
        ret, sMsg = wxcpt.DecryptMsg(reqdata, msg_signature, timestamp, nonce)
        if ret != 0:
            log.warn("ERR: DecryptMsg ret: " + str(ret))
            return ""
        # 解密成功，sMsg即为xml格式的明文
        log.info("[DecryptMsg] ret: %s data: %s  content: %s" % (ret, reqdata, sMsg))
        xml_tree = ET.fromstring(sMsg)
        event = xml_tree.find("Event")
        if event != None:
            #事件
            if event.text.lower() == "click":
                #拉取菜单
                fromuser = xml_tree.find("FromUserName").text
                touser = xml_tree.find("ToUserName").text
                return event_menu_click(xml_tree.find("EventKey").text)
            elif event.text.lower() == "enter_agent":
                fromuser = xml_tree.find("FromUserName").text
                touser = xml_tree.find("ToUserName").text
                text = "你好！%s 欢迎进入钱方好近数据圈！以下是今天的好近日报。查看详情请登陆数据圈。祝您读报愉快！\n\n" % fromuser
                date = (datetime.datetime.now()-datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                text += get_daily_text(date)
                sRespData = "<xml>" \
                          "<ToUserName><![CDATA[%s]]></ToUserName>" \
                          "<FromUserName><![CDATA[%s]]></FromUserName>" \
                          "<CreateTime>%s</CreateTime>" \
                          "<MsgType><![CDATA[text]]></MsgType>" \
                          "<Content><![CDATA[%s]]></Content>" \
                          "</xml>" % (
                    fromuser,
                    touser,
                    timestamp,
                    text
                )
                log.info("wx req data: %s" % (sRespData))
                ret, sEncryptMsg = wxcpt.EncryptMsg(sRespData.encode("utf-8"), nonce, timestamp)
                if ret == 0:
                    return sEncryptMsg
                else:
                    log.warn("ERR: EncryptMsg ret: " + str(ret))
                    return ""
            else:
                return ""
        else:
            #接收消息
            msgtype = xml_tree.find("MsgType").text
            #text消息
            fromuser = xml_tree.find("FromUserName").text
            touser = xml_tree.find("ToUserName").text
            content = xml_tree.find("Content").text
            eventk = "DAILY_HISTORY"
            try:
                # 日期格式则输出该日日报
                date = datetime.datetime.strptime(content.replace(":", "").replace("-", "").replace(" ", ""), "%Y%m%d")\
                    .strftime("%Y-%m-%d")
                log.info(date)
            except:
                date = ""
                eventk = "DAILY_Y"
            return event_menu_click(eventk, date)


class PushMsg(MethodView):
    def get(self):
        """
        发送推送消息
        :return:
        """
        param = request.values
        try:
            totag = param.get("tags", "")
            touser = param.get("users", "")
            toparty = param.get("party", "")
            msgcode = param.get("msgcode", "")
            debug = int(param.get("debug", 0))
        except Exception, e:
            return error(QFRET.PARAMERR, "参数错误")

        #get token
        url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=%s&corpsecret=%s" % (app.config["QY_APPID"], app.config["QY_APPSECRET"])
        req = urlopen(url)
        req_data = req.read()
        json_data = {}
        if req_data:
            try:
                json_data = json.loads(req_data)
                log.info(req_data)
                token = json_data["access_token"]
            except Exception, e:
                return error(QFRET.THIRDERR, respmsg="解析错误: %s" % json_data)

            if debug:
                url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s&debug=1' % token
            else:
                url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s' % token
            content = ""
            if msgcode == "DAILY_Y":
                date = (datetime.datetime.now()-datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                content = get_daily_text(date)
            else:
                return error(QFRET.PARAMERR, "未知msgcode: %s" % msgcode)
            values = {
                "touser": touser,
                "toparty": toparty,
                "totag": totag,
                "msgtype": "text",
                "agentid": 3,
                "text": {
                    "content": content
                },
                "safe": "0"
            }
            data = json.dumps(values, ensure_ascii=False)
            log.info(data)
            req = urllib2.Request(url, data.encode("utf-8"), {'Content-Type': 'application/json'})
            response = urllib2.urlopen(req)
            result = response.read()
            return success(result)
        else:
            return error(QFRET.THIRDERR)