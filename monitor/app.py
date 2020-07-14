#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: soliva
@Site:
@file: application.py
@time: 2020-06-30
@desc:
'''
from flask import Flask, request, render_template, redirect, url_for
import time, os, re, json
import job_monitor
import pandas as pd
from werkzeug.utils import secure_filename
from flask import g
from flask_script import Manager,Server,Command, Option
from gevent.pywsgi import WSGIServer

UPLOAD_FOLDER = '/hongshan/software/zhaohongqiang/monitor'
ALLOWED_EXTENSIONS = ['txt', 'xls',"xlsx",'csv']

def main():
    app = Flask(__name__)
    http_server = WSGIServer(('127.0.0.1', 5000), app)


    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

    @app.route('/', methods=['GET', 'POST'])
    def index():
        print(request.method)
        if request.method == 'GET':

            return render_template('index.html',a=pd.DataFrame())

        elif request.method == 'POST':
            if request.form.get('name'):
                global  date, names
                names= request.form.get('name')
                date= request.form.get('date')
                global flow_cell
                flow_cell = request.form.get('flow_cell')
                # print(names,date,flow_cell)
                try:
                    os.mkdir("/hongshan/software/auto_submit/sub_log/{date}_{names}".format(date=date,names=names))
                    types="成功"
                except:
                    if os.path.exists("/hongshan/software/auto_submit/sub_log/{date}_{names}".format(date=date,names=names)):
                        types = "文件存在"
                    else:
                        types="文件存在或者失败"
                return render_template("index.html",a=pd.DataFrame(),name=names,date=date,flow_cell=flow_cell,types=types)
            if request.files['file']:
                file = request.files['file']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)

                    file.save(os.path.join("/hongshan/software/auto_submit/sub_log/{date}_{names}".format(date=date,names=names), filename))
                    jobs = pd.read_csv(os.path.join("/hongshan/software/auto_submit/sub_log/{date}_{names}".format(date=date,names=names), filename), encoding="gbk", header=None,
                                       names=["panel", "PID", "sample_N", "sample_T", "chip", "name"])
                    jobs=jobs[jobs.name != "数据不全"]

                    def check_list(df):
                        if df["sample_T"] == "yaml无T":
                            return df["sample_N"]
                        elif df["sample_T"] == "CT白细胞-请核查":
                            return df["sample_N"]
                        elif "/" in df["sample_T"]:
                            return df["sample_T"].split("/")[0].strip()
                        else:
                            return df["sample_T"]

                    jobs["check_sample"] = jobs.apply(check_list, axis=1)
                    jobs.to_csv(os.path.join("/hongshan/software/auto_submit/sub_log/{date}_{names}".format(date=date,names=names), "jobs_fillter.csv"))
                    global a, df_ags, df_arg,df_other
                    df_ags, df_arg = job_monitor.main(jobs)
                    df_arg.to_csv(os.path.join("/hongshan/software/auto_submit/sub_log/{date}_{names}".format(date=date,names=names), "arg_result.csv"))
                    df_ags.to_csv(os.path.join(
                        "/hongshan/software/auto_submit/sub_log/{date}_{names}".format(date=date, names=names),
                        "ags_result.csv"))
                    a, df_ags, df_arg,df_other = job_monitor.to_jinja(df_ags, df_arg,jobs)
                    return render_template("index.html",a=a,df_ags=df_ags, df_arg=df_arg,df_other=df_other,
                                            filename=os.path.join(
                        "/hongshan/software/auto_submit/sub_log/{date}_{names}".format(date=date, names=names),
                        filename),name=names,date=date,flow_cell=flow_cell
                                           )


    @app.route('/delags/<NAMES><sample_T>',)
    def delags(NAMES,sample_T):
        global flow_cell, date, names
        global a, df_ags, df_arg,df_other
        # open("/hongshan/software/auto_submit/PC_{flow_cell}.sh".format(**locals()))
        with open(os.path.join("/hongshan/software/auto_submit/sub_log/{date}_{names}".format(date=date,names=names), "ags_del_log.sh"),"a+") as f:
            f.write(f"hand ags delete {NAMES}\n\n")


        # 这个函数可以放你要运行的代码，然后返回相应的值
        return "重投命令以写入arg_del_log.sh\n命令为："+f"hand ags delete {NAMES}"#render_template("index.html", a=a,df_ags=df_ags, df_arg=df_arg,df_other=df_other,)

    @app.route('/delarg/<NAMES><sample_T>',)
    def delarg(NAMES,sample_T):
        global a, df_ags, df_arg,df_other,flow_cell, date, names
        # open("/hongshan/software/auto_submit/PC_{flow_cell}.sh".format(**locals()))
        with open(os.path.join("/hongshan/software/auto_submit/sub_log/{date}_{names}".format(date=date,names=names), "arg_del_log.sh"),"a+") as f:
            f.write(f"hand arg -n sxlj delete {NAMES}\n\n")
        global a, df_ags, df_arg,df_other

        # 这个函数可以放你要运行的代码，然后返回相应的值
        return "重投命令以写入arg_del_log.sh\n命令为："+f"hand arg -n sxlj delete {NAMES}"
        #render_template("index.html", a=a,df_ags=df_ags, df_arg=df_arg,df_other=df_other,)

    @app.route('/restart/<sample_T>')  # 按钮指向的路由
    def restart(sample_T):
        global a,flow_cell

        flow_cell_file = "/hongshan/software/auto_submit/PC_{flow_cell}.sh".format(flow_cell=flow_cell)

        info = os.popen("cat {flow_cell_file} |grep {sample_T} ".format(flow_cell_file=flow_cell_file,sample_T=sample_T)).read()
        print(info)
        with open(os.path.join("/hongshan/software/auto_submit/sub_log/{date}_{names}".format(date=date,names=names), "restart.sh"),"a+") as f:
            f.write(f"{info}\n\n")
        # 这个函数可以放你要运行的代码，然后返回相应的值
        return "重投命令以写入restart.sh\n命令为："+info#render_template("index.html", a=a,df_ags=df_ags, df_arg=df_arg,df_other=df_other,)





    return http_server


if __name__ == '__main__':
    http_server=main()
    http_server.serve_forever()
    # app.debug = True
    # manager = main()
    # manager.add_command("gunicorn", GunicornServer( ))
    # manager.add_command("runserver",Server(host='172.16.36.1' ))
    #
    # manager.run()