# -*- coding: utf-8 -*-
__author__ = 'weather'


def getenvconf(env):
    if env == "develop":
        return Develop
    elif env == "product":
        return Product
    elif env == "local":
        return Local
    else:
        return Config


class Config(object):
    DEBUG = True
    DATE_FORMAT = '%Y-%m-%d'
    DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
    LOGPATH = "../../log/wiseme_info.log"
    NOTEPATH = "../../log/wiseme_note.log"
    SESSION_DIR = "../../flask_session"

    # 微信企业公众平台
    QY_APPID = 'wxd72dd1068904e0c6'
    QY_APPSECRET = '1nDrKL5DlA9OCvGnFgFFvZ_HuSwQ12_q_cAMffiOKFu3M2ajmMwDfwZVlt6DNqj-'
    # 微信开放平台app信息
    WX_APPID = 'wxc07b7237abe59013'
    WX_APPSECRET = '6728c96ff78ff3d318bc328fd2411cd7'
    WX_CALLBACK_DOMAIN = 'data.haojin.in'
    # wx回调token和AESkey
    WX_TOKEN = "peJu9M8jhxgpCU9buJ"
    WX_AESKEY = "Bwew5ALNWopJi1lboErDHUSRGpWQAyTFvMqiSdNZole"
    # o2.qfpay.com app信息
    QF_APPID = 'wxeb6e671f5571abce'
    QF_APPSECRET = '7fe6edd479ca9f47a75f3b395fa9f181'
    QF_CALLBACK_DOMAIN = 'o2.qfpay.com'


    # MYSQL配置
    MYSQL_MAIN_USER = 'qf'
    MYSQL_MAIN_PW = '123456'
    MYSQL_MAIN_DB = 'hadoop_bi'
    MYSQL_MAIN_CHARSET = 'utf8mb4'
    MYSQL_MAIN_HOST = '172.100.102.101'
    MYSQL_MAIN_PORT = 3307
    MYSQL_MAIN = 'mysql+mysqlconnector://{}:{}@{}:{}/{}?charset={}'.format(
        MYSQL_MAIN_USER,
        MYSQL_MAIN_PW,
        MYSQL_MAIN_HOST,
        MYSQL_MAIN_PORT,
        MYSQL_MAIN_DB,
        MYSQL_MAIN_CHARSET
    )
    # NEAR配置
    MYSQL_NEAR_USER = 'qf'
    MYSQL_NEAR_PW = '123456'
    MYSQL_NEAR_DB = 'hadoop_bi'
    MYSQL_NEAR_CHARSET = 'utf8mb4'
    MYSQL_NEAR_HOST = '172.100.102.101'
    MYSQL_NEAR_PORT = 3307
    MYSQL_NEAR = 'mysql+mysqlconnector://{}:{}@{}:{}/{}?charset={}'.format(
        MYSQL_NEAR_USER,
        MYSQL_NEAR_PW,
        MYSQL_NEAR_HOST,
        MYSQL_NEAR_PORT,
        MYSQL_NEAR_DB,
        MYSQL_NEAR_CHARSET
    )
    # mmwd MYSQL配置
    MYSQL_MMWD_USER = 'qf'
    MYSQL_MMWD_PW = '123456'
    MYSQL_MMWD_DB = 'qmm_wx'
    MYSQL_MMWD_CHARSET = 'utf8mb4'
    MYSQL_MMWD_HOST = '172.100.102.152'
    MYSQL_MMWD_PORT = 3306
    MYSQL_MMWD = 'mysql+mysqlconnector://{}:{}@{}:{}/{}?charset={}'.format(
        MYSQL_MMWD_USER,
        MYSQL_MMWD_PW,
        MYSQL_MMWD_HOST,
        MYSQL_MMWD_PORT,
        MYSQL_MMWD_DB,
        MYSQL_MMWD_CHARSET
    )
    # OPENUSER
    OPENUSER_SERVER = {'addr': ('192.20.10.7', 9203), 'timeout': 2000}
    # MongoDB
    MONGODB_HOST_W = '172.100.102.163'
    MONGODB_PORT_W = 27018
    MONGODB_HOST_R = '172.100.102.163'
    MONGODB_PORT_R = 27018
    # psql
    PSQL_DB = "qfdss"
    PSQL_USER = "qfbi_rpts"
    PSQL_PW = "1"
    PSQL_HOST = "172.100.102.156"

    # 外卖详情接口
    DELIVERY_HOST = '172.100.101.151'
    DELIVERY_PORT = 10000
    DELIVERY_APP_CODE = '123456'
    DELIVERY_SERVER_KEY = '123456'


class Local(Config):
    pass


class Develop(Config):
    pass


class Product(Config):
    DEBUG = False
    MONGODB_HOST_W = '192.20.20.11'
    MONGODB_PORT_W = 27017
    MONGODB_HOST_R = '192.20.20.12'
    MONGODB_PORT_R = 27017

    MYSQL_MAIN_USER = 'hadoopbi'
    MYSQL_MAIN_PW = 'bigdata$#@!'
    MYSQL_MAIN_DB = 'hadoop_bi'
    MYSQL_MAIN_CHARSET = 'utf8mb4'
    MYSQL_MAIN_HOST = '192.20.20.12'
    MYSQL_MAIN_PORT = 3306
    MYSQL_MAIN = 'mysql+mysqlconnector://{}:{}@{}:{}/{}?charset={}'.format(
        MYSQL_MAIN_USER,
        MYSQL_MAIN_PW,
        MYSQL_MAIN_HOST,
        MYSQL_MAIN_PORT,
        MYSQL_MAIN_DB,
        MYSQL_MAIN_CHARSET
    )
    # NEAR配置
    MYSQL_NEAR_USER = 'honey_write'
    MYSQL_NEAR_PW = 'FM2015!@#$'
    MYSQL_NEAR_DB = 'near'
    MYSQL_NEAR_CHARSET = 'utf8mb4'
    MYSQL_NEAR_HOST = '192.20.20.7'
    MYSQL_NEAR_PORT = 3306
    MYSQL_NEAR = 'mysql+mysqlconnector://{}:{}@{}:{}/{}?charset={}'.format(
        MYSQL_NEAR_USER,
        MYSQL_NEAR_PW,
        MYSQL_NEAR_HOST,
        MYSQL_NEAR_PORT,
        MYSQL_NEAR_DB,
        MYSQL_NEAR_CHARSET
    )
    MYSQL_MMWD_USER = 'qmm'
    MYSQL_MMWD_PW = 'mMwd2014)$!$'
    MYSQL_MMWD_DB = 'qmm_wx'
    MYSQL_MMWD_CHARSET = 'utf8mb4'
    MYSQL_MMWD_HOST = '192.20.10.5'
    MYSQL_MMWD_PORT = 3306
    MYSQL_MMWD = 'mysql+mysqlconnector://{}:{}@{}:{}/{}?charset={}'.format(
        MYSQL_MMWD_USER,
        MYSQL_MMWD_PW,
        MYSQL_MMWD_HOST,
        MYSQL_MMWD_PORT,
        MYSQL_MMWD_DB,
        MYSQL_MMWD_CHARSET
    )

    # psql
    PSQL_DB = "qfdss"
    PSQL_USER = "qfbi_rpts"
    PSQL_PW = "qfpayreports"
    PSQL_HOST = "192.20.20.9"

    DELIVERY_APP_CODE = '2BD9A875350B4BA78C1549C4AB4CF982'
    DELIVERY_SERVER_KEY = 'D0E47E6F94FA4A1DBD6894052748FC65'
    DELIVERY_HOST = '192.30.2.187'
    DELIVERY_PORT = 6720