# coding=utf-8
import json
import types
import hashlib
import requests
from utils import Storage


class DeliveryHandler(object):
    """
    配送单的处理
    """
    def __init__(self, app_code='', server_key='', host='', port=00, caller='server', timeout=1):
        self.app_code = app_code
        self.server_key = server_key
        self.host = host
        self.port = port
        self.timeout = timeout
        self.caller = caller
        self.goods = []
        self.update_param_fields = ['address', 'goods_name', 'goods_amt', 'goods_content',
            'customer_address', 'customer_name', 'customer_mobile',
            'mchnt_address', 'mchnt_name', 'mchnt_mobile', 'limit_time']

    def _check_params_valid(self, fields, **kwargs):
        """
        检查参数合法性
        :param fields: 允许参数域
        :param kwargs: 真实参数列表
        :return:
        """
        for key in kwargs:
            if key not in fields:
                # log.error('parameters error:%s invalid', key)
                return False
        return True

    def _gen_sign(self, params, charset='utf-8'):
        keys = params.keys()
        keys.sort()
        query = []
        for k in keys:
            if k not in ('sign', 'sign_type'):
                query.append('%s=%s' % (k, params[k]))

        data = '&'.join(query) + self.server_key
        if not isinstance(data, types.UnicodeType):
            data = data.decode(charset)

        md5 = hashlib.md5()
        md5.update(data.encode(charset))
        return md5.hexdigest()

    def add_good(self, goods_name, goods_content='', goods_num=1):
        """
        添加商品
        :param goods_num:商品数量
        :param goods_name:商品名
        :param goods_content:商品备注
        :return:
        """
        data = Storage()
        data.goods_num = goods_num
        data.goods_name = goods_name
        data.goods_content = goods_content
        self.goods.append(data)

    def create(self, order_id, regionid, customer_address, customer_name, customer_mobile,
               mchnt_address, mchnt_name, mchnt_mobile, order_time, limit_time, order_type=1):
        """
        创建配送单
        :param order_id:订单id
        :param order_type：订单类型，1:普通订单, 2:内测订单, 选传（默认为1)
        :param regionid:商圈ID
        :param customer_address:客户地址
        :param customer_name:客户名
        :param customer_mobile:客户手机号码
        :param mchnt_address:商家地址
        :param mchnt_name:商家名称
        :param mchnt_mobile:商家号码
        :param order_time:下单时间
        :param limit_time:送达时间
        :return:
        """
        data = Storage()
        data.orderid = order_id
        data.type = order_type
        data.regionid = regionid
        data.customer_address = customer_address
        data.customer_name = customer_name
        data.customer_mobile = customer_mobile
        data.mchnt_address = mchnt_address
        data.mchnt_name = mchnt_name
        data.mchnt_mobile = mchnt_mobile
        data.order_time = order_time
        data.limit_time = limit_time
        data.goods_info = json.dumps(self.goods)
        data.app_code = self.app_code
        data.sign = self._gen_sign(data)

        url = 'http://{host}:{port}/marathon/disorder/create'.format(host=self.host, port=self.port)
        resp = requests.post(url, data=data, timeout=self.timeout)
        if resp.status_code != 200:
            return {"respcd": resp.status_code}
        ret = json.loads(resp.text)
        return ret

    def update(self, order_id, **kwargs):
        """
        修改配送单
        :param order_id:订单id
        :param kwargs:
        :return:
        """
        if not self._check_params_valid(self.update_param_fields, kwargs):
            raise Exception('parameters error')

        data = Storage()
        data.orderid = order_id
        for key, value in kwargs.iteritems():
            if value:
                data[key] = value
        data.app_code = self.app_code
        data.sign = self._gen_sign(data)

        url = 'http://{host}:{port}/marathon/disorder/edit'.format(host=self.host, port=self.port)
        resp = requests.post(url, data=data, timeout=self.timeout)
        if resp.status_code != 200:
            return {"respcd": resp.status_code}
        ret = json.loads(resp.text)
        return ret

    def query(self, order_ids):
        """
        查询配送单
        :param order_ids: 订单号或者订单号的列表
        :return:
        """
        if not isinstance(order_ids, list):
            raise Exception('parameters error')

        data = Storage()
        data.orderid = json.dumps(order_ids)
        data.app_code = self.app_code
        data.sign = self._gen_sign(data)

        url = 'http://{host}:{port}/marathon/disorder/query'.format(host=self.host, port=self.port)
        resp = requests.get(url, params=data, timeout=self.timeout)
        if resp.status_code != 200:
            return {"respcd": resp.status_code}
        ret = json.loads(resp.text)
        from ..qflogger import log
        log.info("delivery query, url: %s, param: %s, ret: %s" % (url, data, ret))
        return ret

    def get_sessionid(self):
        """
        获取sessionid
        :return:
        """
        data = Storage()
        data.username = 15201287981
        data.password = "123456"
        url = 'http://{host}:{port}/marathon/user/login'.format(host=self.host, port=self.port)
        resp = requests.post(url, params=data, timeout=self.timeout)
        if resp.status_code != 200:
            return {"respcd": resp.status_code}
        cookies = {'sessionid':json.loads(resp.text)['data']['sessionid']}
        return cookies

    def get_analysis(self, cookies):
        """
        获取配送员数据
        :return:
        """
        data = {}
        data['page'] = 0
        data['pagesize'] = 50
        url = 'http://{host}:{port}/marathon/analysis'.format(host=self.host, port=self.port)
        resp = requests.get(url, params=data, cookies=cookies, timeout=self.timeout)
        if resp.status_code != 200:
            return {"respcd": resp.status_code}
        ret = json.loads(resp.text)
        return ret