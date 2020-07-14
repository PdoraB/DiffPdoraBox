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
    # print ("start ags",sample)
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
    '''
    Gevent 处理arg
    :param sample:
    :param arg_list:
    :param num:
    :return:
    '''
    # print ("start ago",sample)
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
    '''
    任务启动器存入列表，然后分别启动，启动后结果存入列表
    :param jobs:
    :return:
    '''
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
        '''
        处理时间d=天，h=小时，m=分钟，s=秒
        :param times:
        :return:
        '''
        if "d" in times:
            return int(times.split("d")[0]) * 24 * 60
        elif "h" in times:
            return int(times.split("h")[0]) * 24
        elif "m" in times:
            return int(times.split("m")[0])
        else:
            return 1


    def contain(df):
        '''
        处理arg的sub状态如果是有空和sub返回，如果是wait或者down不返回
        :param df:
        :return:
        '''

        if  df["NAME"]==None or df["NAME"]==np.nan :
            return True
        else:

            if "sub" in df["NAME"]:
                return  True
            else:
                return False

    def fillter_ags(df,df2):
        '''
        ags 命令 Failed返回failed
        None 返回 none Failed
        其他返回successed

        :param df:
        :param df2:
        :return:
        '''
        sample = df.check
        df_check = df2[df2.check_sample==sample]
        if ("Failed" in df_check["STATUS"].values) :
            return "Failed"
        elif (df_check["STATUS"][df_check["STATUS"].isna()].size>0):

            return "None Failed"
        else:
                return "Successed"

    def fillter_arg(df, df2):
        '''
        arg的sub状态 对每个样本筛选出一个dateframe 然后查询
        sub任务 是否为空
        否返回None Failed
        是判断RUNNING 在 时间大于30m 返回running Failed
        其他返回success
        :param df:
        :param df2:
        :return:
        '''
        sample = df.check

        df_check = df2[df2.check_sample == sample]

        if df_check[df_check.apply(contain,axis=1)].size > 0:
            df_check = df_check[df_check.apply(contain,axis=1)]
            if ("Failed" in df_check["STATUS"].values) or (df_check["STATUS"][df_check["STATUS"].isna()].size > 0):

                return "Failed"
            else:
                if ("Running" in df_check["STATUS"].values) and (df_check["DURATION"][
                                                                     df_check["DURATION"].apply(
                                                                         return_time) > 30].size > 0):
                    return "Running Failed"
                else:
                    return "Successed"
        else:
            return "None Failed"

    def contain_other(df):
        '''
        判断wait 和 down
        :param df:
        :return:
        '''

        if  df["NAME"]==None or df["NAME"]==np.nan :
            return True
        else:

            if "wait" in df["NAME"] or "down" in df["NAME"]:
                return  True
            else:
                return False

    def filter_other(df, df2):
        '''
        与arg other 处理wait 与 down 状态

        :param df:
        :param df2:
        :return:
        '''
        sample = df.check

        df_check = df2[df2.check_sample == sample]

        if df_check[df_check.apply(contain_other, axis=1)].size > 0:
            df_check = df_check[df_check.apply(contain_other, axis=1)]
            if ("Failed" in df_check["STATUS"].values) or (df_check["STATUS"][df_check["STATUS"].isna()].size > 0):

                return "Failed"
            else:
                # print(df_check["STATUS"],df_check["NAME"])
                if ("Running" in df_check["STATUS"].values) and (df_check[df_check["NAME"].str.contains("down")].size >0):
                    return "Down Running"
                else:
                    return "Successed"
        else:
            return "None Failed"

    a=pd.DataFrame({
                        "panel":jobs["panel"],
                         "sample_PID":jobs["PID"],
                        "sample_T":jobs["sample_T"],
                        "sample_N":jobs["sample_N"],
                        "check":jobs["check_sample"],
                    })
    a["ags"] = a.apply(fillter_ags,args=(df_ags,),axis=1)
    a["arg"] = a.apply(fillter_arg, args=(df_arg,), axis=1)
    a["waitordown"] = a.apply(filter_other, args=(df_arg,), axis=1)
    df_other = df_arg[df_arg.apply(contain_other, axis=1)]
    df_arg = df_arg[df_arg.apply(contain,axis=1)]

    return a,df_ags,df_arg,df_other
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
    a, df_ags, df_arg,df_other = to_jinja(df_ags,df_arg,jobs)

