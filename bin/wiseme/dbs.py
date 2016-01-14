# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from mysql.connector.conversion import MySQLConverter
from utils.utils import Storage
import pymongo
import psycopg2


def init_mysqldb(uri):
    """
    初始化数据库连接
    :return:
    """
    sql_engine = create_engine(uri, connect_args={'converter_class': MySQLConverter})
    return sessionmaker(bind=sql_engine, expire_on_commit=False)


def init_mmwddb(uri):
    """
    初始化mmwd数据库连接
    :return:
    """
    sql_engine = create_engine(uri, connect_args={'converter_class': MySQLConverter})
    return sessionmaker(bind=sql_engine, expire_on_commit=False)


def init_neardb(uri):
    """
    初始化near数据库连接
    :return:
    """
    sql_engine = create_engine(uri, connect_args={'converter_class': MySQLConverter})
    return sessionmaker(bind=sql_engine, expire_on_commit=False)


def init_mongo(host, port):
    """
    初始化mongo数据库
    :param host:
    :param port:
    :return:
    """
    return pymongo.MongoClient(host, port, document_class=Storage)


def init_postgre(database="qfdss", user="qfbi_rpts", password="1", host="172.100.102.156"):
    """
    初始化postgresql
    :param database:
    :param user:
    :param password:
    :param host:
    :return:
    """
    return Psession(database, user, password, host)


class Psession:
    def __init__(self, database="qfdss", user="qfbi_rpts", password="1", host="172.100.102.156"):
        self.database = database
        self.user = user
        self.password = password
        self.host = host
        self.conn = None
        self.cur = None

    def connect(self):
        self.conn = psycopg2.connect(database=self.database, user=self.user,
                                     password=self.password, host=self.host)
        self.cur = self.conn.cursor()
        return self.cur

    def close(self):
        self.cur.close()
        self.conn.close()