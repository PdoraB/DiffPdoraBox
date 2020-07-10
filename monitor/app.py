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

UPLOAD_FOLDER = '/hongshan/software/zhaohongqiang/monitor'
ALLOWED_EXTENSIONS = ['txt', 'xls',"xlsx",'csv']

def main(json_file,):
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
                # static_url_path='',
                # # static_folder='../',
                # )
    # f = open(json_file, 'r')
    # foundation_dict = json.load(f)
    # if 'personalise' in foundation_dict:
    #     pass
    # else:
    #     foundation_dict['personalise'] = []
    #
    #     with open(json_file, 'w', ) as f:
    #         f.write(json.dumps(foundation_dict, encoding='UTF-8', ensure_ascii=False))

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
                names= request.form.get('name')
                date= request.form.get('date')
                global flow_cell
                flow_cell = request.form.get('flow_cell')
                print(names,date,flow_cell)
                try:
                    os.mkdir("./{date}_{names}".format(**locals()))
                    types="成功"
                except:
                    types="文件存在或者失败"
                return render_template("index.html",a=pd.DataFrame(),name=names,date=date,flow_cell=flow_cell,types=types)
            if request.files['file']:
                file = request.files['file']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    jobs = pd.read_csv(filename, encoding="gbk", header=None,
                                       names=["panel", "PID", "sample_N", "sample_T", "chip", "name"])
                    def check_list(df):
                        if df["sample_T"] == "yaml无T":
                            return df["sample_N"]
                        else:
                            return df["sample_T"]

                    jobs["check_sample"] = jobs.apply(check_list, axis=1)
                    global a, df_ags, df_arg
                    df_ags, df_arg = job_monitor.main(jobs)

                    a, df_ags, df_arg = job_monitor.to_jinja(df_ags, df_arg,jobs)
                    return render_template("index.html",a=a,df_ags=df_ags, df_arg=df_arg,
                                            filename=filename)


    @app.route('/delags/<NAMES>',)
    def delags(NAMES):
        global flow_cell
        # open("/hongshan/software/auto_submit/PC_{flow_cell}.sh".format(**locals()))
        print(f"hand ags delete {NAMES}")
        global a, df_ags, df_arg
        # 这个函数可以放你要运行的代码，然后返回相应的值
        return render_template("index.html", a=a,df_ags=df_ags, df_arg=df_arg,)
    @app.route('/delarg/<NAMES>',)
    def delarg(NAMES):
        global flow_cell
        # open("/hongshan/software/auto_submit/PC_{flow_cell}.sh".format(**locals()))
        print(f"hand arg -n sxlj delete {NAMES}")
        global a, df_ags, df_arg
        # 这个函数可以放你要运行的代码，然后返回相应的值
        return render_template("index.html", a=a,df_ags=df_ags, df_arg=df_arg,)

    @app.route('/hello')  # 按钮指向的路由
    def hello():
        global a
        # 这个函数可以放你要运行的代码，然后返回相应的值
        return render_template("index.html",a=a)




    return app


if __name__ == '__main__':
    # jobs = pd.read_csv("./job.csv", encoding="gbk", header=None,
    #                    names=["panel", "PID", "sample_N", "sample_T", "chip", "name"])
    #
    #
    # def check_list(df):
    #     if df["sample_T"] == "yaml无T":
    #         return df["sample_N"]
    #     else:
    #         return df["sample_T"]
    #
    #
    # jobs["check_sample"] = jobs.apply(check_list, axis=1)
    #
    # ags_list, arg_list = job_monitor.main()
    # a = pd.DataFrame({
    #     "sample_PID": jobs["PID"],
    #     "sample_T": jobs["sample_T"],
    #     "sample_N": jobs["sample_N"],
    #     "ags_result": ags_list,
    #     "arg_result": arg_list,
    #     "arg_sub": jobs["sample_N"],
    #     "arg_wait": jobs["sample_N"],
    #     "check": jobs["check_sample"],
    #
    # })
    #
    #
    # def split_df(df):
    #     if df["arg_result"] != 'None':
    #
    #         return [i for i in df["arg_result"] if "sub" in i][0]
    #     else:
    #         return "None"
    #
    #
    # a["ago_sub"] = a.apply(split_df, axis=1)
    # print(a)
    # a.to_csv("test.csv")
    # a=pd.read_csv("test.csv")
    # print(a)
    app = main('test')
    app.run(host='172.16.36.1')