# -*- coding: utf-8 -*-
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, Date


Base = declarative_base()

class HJFPopulation(Base):
    """
    haojin 汇总
    """
    __tablename__ = 'hj_f_population'

    c_yearmonthday = Column(String, primary_key=True)
    c_year = Column(String)
    c_yearmonth = Column(String)

    topic_day_cnt = Column(Integer)
    topic_cnt = Column(Integer)

    post_day_cnt = Column(Integer)
    post_cnt = Column(Integer)

    user_day_cnt = Column(Integer)
    user_cnt = Column(Integer)

    commnets_day_cnt = Column(Integer)
    comments_cnt = Column(Integer)

    pv = Column(Integer)
    uv = Column(Integer)

    active_user_cnt = Column(Integer)

    sale_day_cnt = Column(Float)
    sale_cnt = Column(Float)
    sale_day_amt = Column(Float)
    sale_amt = Column(Float)

    average_post_cnt = Column(Integer)
    average_post_likes = Column(Float)

    qiye_num = Column(Integer)
    qiye_amt = Column(Float)
    zx_num = Column(Integer)
    zx_amt = Column(Float)
    soho_num = Column(Integer)
    soho_amt = Column(Float)
    tm_num = Column(Integer)
    tm_amt = Column(Float)
    dh_num = Column(Integer)
    dh_amt = Column(Float)
    wx_num = Column(Integer)
    wx_amt = Column(Float)

    def to_dict(self):
        ret_dict = {}
        for c in self.__table__.columns:
            cvalue = getattr(self, c.name, "")
            if isinstance(cvalue, unicode):
                cvalue = cvalue.encode("utf8")
            ret_dict[c.name] = cvalue
        return ret_dict

    Base.to_dict = to_dict


class HJFUser(Base):
    """
    haojin 用户
    """
    __tablename__ = 'hj_f_user'

    user_id = Column(Integer, primary_key=True)

    c_yearmonthday = Column(String)
    c_year = Column(String)
    c_yearmonth = Column(String)

    nick_name = Column(String)
    create_time = Column(DateTime)
    update_time = Column(DateTime)
    country = Column(String)
    province = Column(String)
    city = Column(String)
    gender = Column(String)
    union_id = Column(String)
    signature = Column(String)
    avatar = Column(String)
    mobile = Column(String)
    topic_cnt = Column(Integer)
    post_cnt = Column(Integer)
    likes_cnt = Column(Integer)
    comments_cnt = Column(Integer)
    pv = Column(Integer)

    last_view_date = Column(Date)
    last_buy_date = Column(Date)
    last_view_time = Column(DateTime)
    last_buy_time = Column(DateTime)

    sale_cnt = Column(Integer)
    sale_amt = Column(Float)
    order_cnt = Column(Integer)
    order_amt = Column(Float)

    mark = Column(Integer)
    mark_name = Column(String)

    def to_dict(self):
        ret_dict = {}
        for c in self.__table__.columns:
            cvalue = getattr(self, c.name, "")
            if isinstance(cvalue, unicode):
                cvalue = cvalue.encode("utf8")
            ret_dict[c.name] = cvalue
        return ret_dict

    @staticmethod
    def getitem(item):
        return HJFUser.__getattribute__(HJFUser, item)

    Base.to_dict = to_dict