#!/usr/bin/env pn
# -*- coding: utf-8 -*-
'''
@ar: soliva
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
import numpy as np
import sys,re
from io import StringIO



def func_ags(sample,ags_list,num):
    '''
    Gevent 处理 ags 命令 并行化
    :param sample: 样本编号
    :param ags_list: ags_list
    :param num: 样本列表
    :return: ags_list
    '''
    print ("start ags",sample)
    # with open("out.txt","a+") as f :
        # subprocess.call("hand ags list|grep -i W067750T",shell=True)
    sub = subprocess.Popen(f"hand ags list|grep -i {sample}",stdout=subprocess.PIPE,shell=True)#
    # print(sub.stdout)


    out,err= sub.communicate()
    # ags_list.append(out.decode('utf-8'))
    if out.decode('utf-8')=="":
        num.append(sample)
        ags_list.append("None")
        # f.write("None\n")
    else:
        num.append(sample)
        ags_list.append(out.decode('utf-8'))
        # f.write(out.decode('utf-8'))

def func_arg(sample,arg_list,num):
    print ("start ago",sample)
    # subprocess.call("hand ags list|grep -i W067750T",shell=True)
    sub = subprocess.Popen(f"hand aro list -n sxlj|grep -i {sample}", stdout=subprocess.PIPE,shell=True)
    out,err = sub.communicate()
    # print(out)
    if out.decode('utf-8')=="":
        num.append(sample)
        arg_list.append("None")
        # f.write("None\n")
    else:
        num.append(sample)
        arg_list.append(out.decode('utf-8'))
def main(jobs):
    job_list_arg = []
    arg_list = []
    arg_num = []
    for i in jobs["check_sample"]:
        job_list_arg.append(gevent.spawn(func_arg, i, arg_list, arg_num))
    gevent.joinall(job_list_arg)
    df_arg = pd.DataFrame()
    for run, names in zip(arg_list, arg_num):
        if run == "None":
            df_arg = df_arg.append(pd.DataFrame({
                "check_sample": names,
                "NAME": None,
                "STATUS": None,
                "AGE": None,
                "DURATION": None,
                "PRIORITY": None
            }, index=[0]))
        else:
            df = pd.read_table(StringIO(run), header=None, sep="\s+",
                               names=["NAME", "STATUS", "AGE", "DURATION", "PRIORITY"])
            df["check_sample"] = names
            df_arg = df_arg.append(df)




    job_list_ags = []
    ags_list=[]
    ags_num=[]
    for i in jobs["check_sample"]:
        job_list_ags.append(gevent.spawn(func_ags, i,ags_list,ags_num))
    gevent.joinall(job_list_ags)
    df_ags = pd.DataFrame()
    for run, names in zip(ags_list, ags_num):
        if run == "None":
            df_ags = df_ags.append(pd.DataFrame({
                "check_sample": names,
                "NAME": None,
                "STATUS": None,
                "AGE": None,
                "DURATION": None,
                "PRIORITY": None
            }, index=[0]))
        else:
            df = pd.read_table(StringIO(run), header=None, sep="\s+",
                               names=["NAME", "STATUS", "AGE", "DURATION", "PRIORITY"])
            df["check_sample"] = names
            df_ags = df_ags.append(df)
    return df_ags,df_arg


def to_jinja(df_ags,df_arg,jobs):
    def return_time(times):
        if "d" in times:
            return int(times.split("d")[0]) * 24 * 60
        elif "h" in times:
            return int(times.split("h")[0]) * 24
        else:
            return int(times.split("m")[0])


    def fillter_ags(df,df2):
        sample = df.check
        df_check = df2[df2.check_sample==sample]
        if ("Failed" in df_check["STATUS"].values) or (df_check["STATUS"][df_check["STATUS"].isna()].size>0):

            return "Failed"
        else:
                return "Successed"

    def fillter_arg(df, df2):
        sample = df.check
        df_check = df2[df2.check_sample == sample]

        if ("Failed" in df_check["STATUS"].values) or (df_check["STATUS"][df_check["STATUS"].isna()].size>0):

            return "Failed"
        else:
            if "Running" in list(df_check["STATUS"]) and df_check["DURATION"][
                df_check["DURATION"].apply(return_time) > 30].size > 0:
                return "Failed"
            else:
                return "Successed"

    a=pd.DataFrame({
         "sample_PID":jobs["PID"],
        "sample_T":jobs["sample_T"],
        "sample_N":jobs["sample_N"],
        "check":jobs["check_sample"],
    })
    a["ags"] = a.apply(fillter_ags,args=(df_ags,),axis=1)
    a["arg"] = a.apply(fillter_arg, args=(df_arg,), axis=1)
    return a,df_ags,df_arg
if __name__ == '__main__':
    jobs = pd.read_csv("./job.csv",encoding="gbk",header=None,names=["panel","PID","sample_N","sample_T","chip","name"])
    def check_list(df):
        if df["sample_T"]=="yaml无T":
            return df["sample_N"]
        else:
            return df["sample_T"]
    jobs["check_sample"] = jobs.apply(check_list,axis=1)
    df_ags,df_arg=main(jobs)
    print(df_ags,df_arg)
    a, df_ags, df_arg = to_jinja(df_ags,df_arg,jobs)

    # def split_df(df):
    #     if df["arg_result"] != 'None':
    #
    #         return [i for i in df["arg_result"] if "sub" in i]
    #     else:
    #         return "None"
    # a["ago_sub"]=a.apply(split_df,axis=1)
    # e=a.drop('ags_result', axis=1).join(
    #     a['ags_result'].str.split('/', expand=True).stack().reset_index(level=1, drop=True).rename('ags_result'))
    # print(e)