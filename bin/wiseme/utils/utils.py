# -*- coding: utf-8 -*-
import gevent
import json
import datetime
from copy import deepcopy
from numbers import Number

from bson import ObjectId
from flask import copy_current_request_context


class Storage(dict):
    """
    A Storage object is like a dictionary except `obj.foo` can be used in addition to `obj['foo']`.
        >>> o = storage(a=1)
        >>> o.a
        1
        >>> o['a']
        1
        >>> o.a = 2
        >>> o['a']
        2
        >>> del o.a
        >>> o.a
        Traceback (most recent call last):
            ...
        AttributeError: 'a'
    """

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as k:
            raise AttributeError(k)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError as k:
            raise AttributeError(k)

    def __repr__(self):
        return '<Storage ' + dict.__repr__(self) + '>'


def recursive_json_loads(data):
    """
    将 json 字符串迭代处理为 Python 对象
        >>> a = '[{"foo": 1}]'
        >>> b = recursive_json_loads(a)
        >>> b[0].foo
        >>> 1
    """
    if isinstance(data, list):
        return [recursive_json_loads(i) for i in data]
    elif isinstance(data, tuple):
        return tuple([recursive_json_loads(i) for i in data])
    elif isinstance(data, dict):
        return Storage({recursive_json_loads(k): recursive_json_loads(data[k]) for k in data.keys()})
    else:
        try:
            obj = json.loads(data)
            if obj == data:
                return data
            return recursive_json_loads(obj)
        except:
            return data


def model2dict(model, datetime_format=None):
    """
    本函数用于使对象可 json 序列化，且返回的字典都是新的（deepcopy）
    """
    if isinstance(model, dict):
        model = Storage(deepcopy(model))
        to_pop = []
        for k in model:
            # 过滤
            if isinstance(k, basestring) and (k.startswith('_') or k.isupper()):
                to_pop.append(k)
                continue
            # 转换
            elif isinstance(model[k], datetime.datetime):
                model[k] = model[k].strftime(datetime_format) if datetime_format else model[k].isoformat(' ')
            elif isinstance(model[k], ObjectId):
                model[k] = str(model[k])
            # 递归
            else:
                model[k] = model2dict(model[k], datetime_format)
        for k in to_pop:
            model.pop(k)
        return model
    elif hasattr(model, '__dict__') and not isinstance(model, Number):
        return model2dict(model.__dict__, datetime_format)
    elif isinstance(model, (list, tuple)):
        return [model2dict(m, datetime_format) for m in model]
    else:
        return model


def dict_project(data, map_rulls={}):
    """
    字典投影，支持取 data 的子集和改名。只想投影而不想改名的，写个 1 就行，eg：
        >>> data
        {'a': 1,
         'b': 2,
         'c': 3}
        >>> map_rulls
        {'a': 'x',
         'c': 1}
        >>> dict_project(data, map_rulls)
        {'x': 1,
         'c': 3}
    """
    if isinstance(data, dict):
        data = Storage({map_rulls[k] if isinstance(map_rulls[k], basestring) else k: data[k] for k in data if k in map_rulls})
    elif isinstance(data, (list, tuple)):
        return [dict_project(o, map_rulls) for o in data]
    else:
        raise ValueError('无法处理对象: %s' % str(data))
    return data


def model2dict_x(obj, keys=None):
    """
    获取指定keys的字典
    keys=None 返回所有属性的字典
    """
    if keys is None:
        if isinstance(obj, dict):
            return obj
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            raise ValueError('无法处理对象: {0}'.format(str(obj)))

    elif isinstance(keys, list):
        ret = {}
        if isinstance(obj, dict):
            for key in keys:
                ret[key] = obj.get(key, None)
        elif hasattr(obj, '__dict__'):
            obj_dict = obj.__dict__
            for key in keys:
                ret[key] = obj_dict.get(key, None)
                if not ret[key] or ret[key] == 'None':
                    ret[key] = ''
        else:
            raise ValueError('无法处理对象: {0}'.format(str(obj)))
    else:
        raise TypeError('参数类型错误')

    return ret


def i_have_a_dream(func, *args, **kwargs):
    """
    异步任务处理。本函数会立即返回，并使用 gevent 的新线程执行 func 函数（带上下文）。
    """
    return gevent.spawn(copy_current_request_context(func), *args, **kwargs)

class Storage(dict):
    """
    A Storage object is like a dictionary except `obj.foo` can be used in addition to `obj['foo']`.
        >>> o = storage(a=1)
        >>> o.a
        1
        >>> o['a']
        1
        >>> o.a = 2
        >>> o['a']
        2
        >>> del o.a
        >>> o.a
        Traceback (most recent call last):
            ...
        AttributeError: 'a'
    """

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as k:
            raise AttributeError(k)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError as k:
            raise AttributeError(k)

    def __repr__(self):
        # return '<Storage ' + dict.__repr__(self) + '>'
        return dict.__repr__(self)