# -*- coding: utf-8 -*-
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, SMALLINT
from sqlalchemy.dialects.mysql import TINYINT
import datetime

Base = declarative_base()


class Order(Base):
    """
    商户订单
    """
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    cusid = Column(Integer)         # C端用户ID
    openid = Column(String(50))     # 消费者
    weixin_mp = Column(Integer, default=0)     # 微信公众账号
    fakeid = Column(String(50))     # 消费者fakeid
    goodid = Column(Integer)
    good_name = Column(String(50))
    good_img = Column(String(200))
    # good = relationship(Good, primaryjoin=(goodid==Good.id))
    good = None
    detailid = Column(Integer)      # 规格配置ID
    good_size = Column(String(50))      # 规格详情
    province = Column(String(50))       # 省
    city = Column(String(50))           # 市
    address = Column(String(50))        # 送货地址
    zipcode = Column(String(50))        # 邮政编码
    consignee = Column(String(500))     # 收货人
    contact = Column(String(500))       # 联系人
    telephone = Column(String(500))     # 联系电话
    weixinid = Column(String(50))     # 微信号
    amount = Column(Integer)        # 数量
    payable = Column(Float())           # 应付款
    postage = Column(Integer)       # 邮费
    origin_payable = Column(Integer)           # 原始价格
    payable_int = Column(Integer)           # 应付款 INT存储
    paytype = Column(Integer)       # 付款方式
    shiptype = Column(Integer)      # 送货方式
    status = Column(Integer)        # 20140104 新增, 订单状态。
    pay_status = Column(Integer)    # 0 未付款 1 已付款
    ship_status = Column(Integer)    # 0 未发货 1 已发货
    pay_chnl = Column(Integer)          # 20140108 新增, 支付方式 -1: 未支付 0:易宝 1:百度钱包 2:支付宝 3:微信支付
    pay_orderid = Column(String(32))          # 20140108 新增, 订单号 self.id + time_str
    pay_syssn = Column(String(32))          # 20140108 新增, 支付渠道交易流水号
    ship_carrier = Column(String(32))          # 20140108 新增, 物流公司
    ship_trackno = Column(String(64))          # 20140108 新增, 物流跟踪编号
    remark = Column(String(300))        # 备注
    pay_time = Column(DateTime, nullable=True)  # 付款时间
    ship_time = Column(DateTime, nullable=True)  # 20140108 新增，发货时间
    create_time = Column(DateTime)          # 首次时间
    update_time = Column(DateTime)          # 更新时间
    order_type = Column(Integer)        #订单类型 0为普通订单，2 为担保交易 3 为兑换订单(好近特卖兑换) 5:好近折扣卡买单 6：外卖订单
    qf_uid = Column(Integer)
    agency_type = Column(Integer)       # 代理类型  10 自营 20 购买式代理  30 一件代发
    source = Column(SMALLINT)           # 订单来源  0： 喵喵成单， 1：好近特卖， 2: 企业折扣卡买单
    confirm_status = Column(Integer)    # 确认付款状态 10 未确认付款  20 买家确认付款  21 买家申请退款   30  系统自动确认付款
    confirm_time = Column(DateTime)      # 确认时间
    settle_status = Column(Integer)     # 结算状态  0 为初始化  1 可结算  2  退款冻结
    busi_status = Column(Integer)       # 款项最终状态   10 未结算   11 已结算  20 退款中  21  已退款
    activity_id = Column(Integer)       # 好近活动 id
    accept_time = Column(DateTime)      # 商户确认接单时间

    def __init__(self, openid, cusid=-1):
        self.cusid = cusid
        self.openid = openid
        self.fakeid = -1
        self.goodid = -1      # 新订单类型，商品详情在 订单详情中，goodid 默认为-1
        self.paytype = 0
        self.status = Order_Consts.STATE_PLACED
        self.pay_chnl = -1
        timenow = datetime.datetime.now()
        self.create_time = timenow
        self.update_time = timenow
        self.pay_status = 0
        self.ship_status = 0
        self.agency_type = Order_Consts.AGENCY_SELL
        self.source = Order_Consts.SOURCE_NORMAL
        self.order_type = Order_Consts.TYPE_NORMAL
        self.confirm_status = Order_Consts.CONFIRM_PLACED
        self.settle_status = Order_Consts.SETTLE_PLACED
        self.busi_status = Order_Consts.BUSI_PLACED

    def to_dict(self):
        ret_dict = {}
        for c in self.__table__.columns:
            cvalue = getattr(self, c.name, "")
            if isinstance(cvalue, unicode):
                cvalue = cvalue.encode("utf8")
            ret_dict[c.name] = cvalue
        return ret_dict


class OrderDetail(Base):
    """
    订单详情
    """
    __tablename__ = 'order_detail'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer)      # 订单id
    iid = Column(Integer)           # 商品id
    title = Column(String(50))      # 商品名称
    skuid = Column(Integer)         # sku id
    img = Column(String(100))       # 商品图片
    specs = Column(String(100))     # 商品规格
    descr = Column(String(500))     # 商品描述
    amount = Column(Integer)        # 订购数量
    price = Column(Integer)         # 付款价格
    is_panic = Column(TINYINT)      # 是否为抢购
    create_time = Column(DateTime)  # 创建时间
    update_time = Column(DateTime)  # 更新时间

    def __init__(self, order_id):
        self.order_id = order_id
        now = datetime.datetime.now()
        self.create_time = now
        self.update_time = now

    def to_dict(self):
        ret_dict = {}
        for c in self.__table__.columns:
            cvalue = getattr(self, c.name, "")
            if isinstance(cvalue, unicode):
                cvalue = cvalue.encode("utf8")
            ret_dict[c.name] = cvalue
        return ret_dict


class OrderNear(Base):
    """
    好近订单
    """
    __tablename__ = 'order_near'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer)  # 订单id
    topic_id = Column(String(32))  # 话题id
    near_uid = Column(Integer)  # 好近用户id
    create_time = Column(DateTime)
    update_time = Column(DateTime)

    def __init__(self, order_id):
        self.order_id = order_id
        now = datetime.datetime.now()
        self.create_time = now
        self.update_time = now

    def to_dict(self):
        ret_dict = {}
        for c in self.__table__.columns:
            cvalue = getattr(self, c.name, "")
            if isinstance(cvalue, unicode):
                cvalue = cvalue.encode("utf8")
            ret_dict[c.name] = cvalue
        return ret_dict


class OrderOperating(Base):
    """
    订单变更详情记录
    """
    __tablename__ = 'order_operating'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer)     # 订单ID
    operate_type = Column(Integer)      # 订单操作类型
    operate_time = Column(DateTime)          # 操作时间
    payable_change = Column(String(50))      # 价格变更记录

    def __init__(self, order_id, operate_type):
        self.order_id = order_id
        self.operate_type = operate_type
        self.operate_time = datetime.datetime.now()

    def to_dict(self):
        ret_dict = {}
        for c in self.__table__.columns:
            cvalue = getattr(self, c.name, "")
            if isinstance(cvalue, unicode):
                cvalue = cvalue.encode("utf8")
            ret_dict[c.name] = cvalue
        return ret_dict


# 常量
class Order_Consts(object):
    """
    订单常量类
    """
    STATE_PLACED = 1    # 代付款 订单生成
    STATE_PAYED = 2     # 已付款
    STATE_CONFIRM = 3   # 已确认 未使用
    STATE_OLD_SHIPPED = 4   # 已发货（旧版已发货，当已完成处理)
    STATE_SHIP = 5      # 已发货 (好近中，等同 快递员已取单)
    STATE_RECEIVED = 6  # 已收货
    STATE_COMMENT = 7   # 已评价 未使用
    STATE_REFUND = 8    # 申请退款
    STATE_REFUND_FINISHED = 9  # 退款订单完成
    STATE_FINISHED = 10  # 已完成 未使用
    STATE_SYS_CLOSED = 11  # 系统关闭
    STATE_CANCEL = 90   # 消费者撤销
    STATE_CLOSED = 80   # 商户关闭

    TYPE_NORMAL = 0
    TYPE_RECEIPT = 1
    TYPE_GUARANTEE = 2
    TYPE_REDEEM = 3  # 特卖
    TYPE_COUPON = 4  # 优惠券 分众
    TYPE_CDCPAY = 5  # 买单
    TYPE_TAKEOUT = 6  # 外卖

    PAY_YEEPAY = 0
    PAY_BAIPAY = 1
    PAY_ALIPAY = 2
    PAY_WXPAY = 31
    PAY_GRAYAUTOPAY = 9
    PAY_QTPAY_H5 = 10
    PAY_QTPAY_APP = 11

    CONFIRM_PLACED = 10
    CONFIRM_NORMALPAY = 20
    CONFIRM_REFUND_APPLY = 21
    CONFIRM_AOTOPAY = 30
    CONFIRM_REFUND_FAIL_BY_SYS = 31
    CONFIRM_REFUND_FAIL_BY_SERVICE = 32

    SETTLE_PLACED = 0
    SETTLE_AVAILABLE = 1
    SETTLE_REFUND_FREEZE = 2

    BUSI_PLACED = 10
    BUSI_SETTLED = 11
    BUSI_REFUNDING = 20
    BUSI_REFUNDED = 21

    AGENCY_SELL = 10
    AGENCY_RESELL = 20
    AGENCY_AGENCY = 30

    SOURCE_NORMAL = 0
    SOURCE_HAOJIN = 1
    SOURCE_CDCPAY = 2
    SOURCE_FZ = 3

    # 送货类型
    SHIPTYPE_SELF = 1   # 自取
    SHIPTYPE_DELIVER = 2   # 送货

    SHIP_STATUS_FALSE = 0
    SHIP_STATUS_TRUE = 1

    IS_PAYED = 1
    NOT_PAYED = 0