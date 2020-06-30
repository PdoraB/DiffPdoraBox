#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: soliva
@Site: 
@file: job_monitor.py
@time: 2020-06-29
@desc:
'''
from gevent import monkey
monkey.patch_all()
import gevent
import os
import subprocess

def func(num):
    print ("start", num)
    subprocess.call(['sleep', '3'])
    # sub = subprocess.Popen(['sleep 3'], shell=True)
    # out, err = sub.communicate()
    print ("end", num)

g1 = gevent.spawn(func, 1)
g2 = gevent.spawn(func, 2)
g3 = gevent.spawn(func, 3)
g1.join()
g2.join()
g3.join()
