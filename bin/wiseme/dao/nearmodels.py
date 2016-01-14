# -*- coding: utf-8 -*-
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, MetaData, SmallInteger


Base = declarative_base()

class NearBase(Base):
    __abstract__ = True
    __shard__ = 'near'
    metadata = MetaData()

class ShopOwnerModel(NearBase):
    """
    实体店
    """
    __tablename__ = "shop_owner"
    id = Column(Integer, primary_key=True)
    qf_uid = Column(Integer)
    nearshop_id = Column(String(50))
    status = Column(SmallInteger, default=1)

    def __init__(self, **kwargs):
        return super(ShopOwnerModel, self).__init__(**kwargs)

    def to_dict(self):
        ret_dict = {}
        for c in self.__table__.columns:
            cvalue = getattr(self, c.name, "")
            if isinstance(cvalue, unicode):
                cvalue = cvalue.encode("utf8")
            ret_dict[c.name] = cvalue
        return ret_dict

