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
import pandas as pd
import sqlite3
import sys,re

jobs = pd.read_csv("./job.csv",encoding="gbk",header=None,names=["panel","PID","sample_N","sample_T","chip","name"])
def check_list(df):
    if df["sample_T"]=="yaml无T":
        return df["sample_N"]
    else:
        return df["sample_T"]
jobs["check_sample"] = jobs.apply(check_list,axis=1)

def func(sample):
    print ("start",sample)
    # subprocess.call("hand ags list|grep -i W067750T",shell=True)
    sub = subprocess.Popen(f"hand ags list|grep -i {sample}", shell=True)
    out, err = sub.communicate()





job_list=[]

for i in jobs["check_sample"]:
    job_list.append(gevent.spawn(func, i))

gevent.joinall(job_list)