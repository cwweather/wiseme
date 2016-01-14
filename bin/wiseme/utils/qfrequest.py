# -*- coding: utf-8 -*-

import time
import json
import traceback
import re
from flask import request, g
from utils import recursive_json_loads, model2dict
from ..qflogger import note_log

def handle_before_request(sender, **extra):
    """
    请求开始时的日志
    """
    # 标记请求开始时间
    g.start = time.time()
    headers = {}
    headers.update(request.headers)
    if headers.get('Cookie'):
        split_pattern = '; ?'
        kv_pattern = '(.+)=(.*)'
        cookies = re.split(split_pattern, headers['Cookie'])
        for i in range(len(cookies)):
            kv_paire = re.match(kv_pattern, cookies[i])
            if kv_paire:
                cookies[i] = {kv_paire.group(1): kv_paire.group(2)}
        headers['Cookie'] = cookies
    args = {}
    form = {}
    for k, v in request.args.iteritems():
        args.update({k: v})
    for k, v in request.form.iteritems() or request.json.iteritems() or {}:
        form.update({k: v})
    # buffer note log
    note_args = {}
    note_args.update(args)
    note_args.update(form)
    g.note_log = {
        'method': request.method,
        'host': request.host,
        'path': request.path,
        'remote_ip': request.headers.get('X-Forwarded-For', '').split(',')[0] or request.remote_addr,
        'args': note_args,
        'UA': headers.get('User-Agent'),
    }


def send_remote_log_tail(sender, **extra):
    """
    请求结束时发送 BI 日志
    """
    log_message = {}
    log_message.update({'user_id': getattr(request, 'user_id', None), 'host': request.host})
    if 'exception' in extra:
        log_message.update({'status': 500})
        log_message.update({'exception': traceback.format_exc()})
    if 'response' in extra:
        response = extra['response']
        log_message.update({'status': response.status_code})
        if response.mimetype == 'application/json':
            data = recursive_json_loads(response.data)
            if isinstance(data, dict):
                log_message.update({'respcd': data.get('respcd')})
                log_message.update({'resperr': data.get('resperr')})
                log_message.update({'respmsg': data.get('respmsg')})
                log_message.update({'ret': data})
        headers = {}
        headers.update(response.headers)
        log_message.update({'headers': headers})
    # buffer note log
    g.note_log.update({
        'status': log_message.get('status'),
        'respcd': log_message.get('respcd'),
        'ret': log_message.get('ret'),
        'exception': log_message.get('exception'),
        'duration': '%.0fms' % ((time.time() - g.start)*1000),
    })
    note_logs = []
    for k in ('method', 'path', 'host', 'status', 'respcd', 'remote_ip', 'duration', 'UA', 'args'):
        note_logs.append(g.note_log[k])
    note_logs = [json.dumps(note) if not isinstance(note, basestring) else note for note in note_logs]
    note_log.info('|'.join(note_logs))
    if g.note_log['exception']:
        note_log.error(g.note_log['exception'])