#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: soliva
@Site: 
@file: config.py.py
@time: 2020-06-29
@desc:
'''
class Config(object):
    # 开关
    SCHEDULER_API_ENABLED = True
    # 持久化配置
    SCHEDULER_JOBSTORES = {
            'default': SQLAlchemyJobStore(url='sqlite:///flask_context.db')
        }
    SCHEDULER_EXECUTORS = {
        'default': {'type': 'threadpool', 'max_workers': 20}
    }