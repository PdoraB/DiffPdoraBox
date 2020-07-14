#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: soliva
@Site: 
@file: www.py
@time: 2020-06-30
@desc:
'''
from application import app
from webs.controllers.index import route_index

app.register_blueprint( route_index,url_prefix = "/" )
