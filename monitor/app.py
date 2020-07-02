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
import time, os, re, pandas, json


def main(json_file, FILE_DIR):
    app = Flask(__name__,
                # template_folder='/gpfs1/RD_project/zhaohongqiang/project/bin/Multi_omics_analysis/Report/',
                static_url_path='',
                # static_folder='../',
                )
    f = open(json_file, 'r')
    foundation_dict = json.load(f)
    if 'personalise' in foundation_dict:
        pass
    else:
        foundation_dict['personalise'] = []
        print
        foundation_dict['personalise']
        with open(json_file, 'w', ) as f:
            f.write(json.dumps(foundation_dict, encoding='UTF-8', ensure_ascii=False))
    os.system('ln -sf {} {}'.format(FILE_DIR,
                                    os.path.split(os.path.realpath(__file__))[0] + '/static', ))

    @app.route('/', methods=['GET', 'POST'])
    def index():

        if request.method == 'GET':
            return render_template('index.html', greeting_list=zip(foundation_dict['personalise'],
                                                                   range(len(foundation_dict['personalise']) + 1)))
        else:
            if 'add' in request.form:
                project_name = request.form.get('name')
                png_dir = request.form.get('comment').split('||')
                data_file = request.form.get('input_text').split('||')
                project_anno = request.form.get('project')
                png_anno = request.form.get('png_anno')

                foundation_dict['personalise'].append({"project_name": project_name,
                                                       'png_dir': png_dir,
                                                       'data_file': data_file,
                                                       'project_anno': project_anno,
                                                       'png_anno': png_anno

                                                       })
                with open(json_file, 'w', ) as f:
                    f.write(json.dumps(foundation_dict, encoding='UTF-8', ensure_ascii=False, indent=4))
                return redirect(url_for('index'))
            elif 'remove' in request.form:
                foundation_dict['personalise'].pop()
                with open(json_file, 'w', ) as f:
                    f.write(json.dumps(foundation_dict, encoding='UTF-8', ensure_ascii=False, indent=4))
                return redirect(url_for('index'))

    return app


if __name__ == '__main__':
    app = main('test')
    app.run(host='0.0.0.0')