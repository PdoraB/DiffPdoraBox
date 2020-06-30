#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: soliva
@Site:
@file: config.py
@time: 2020-05-16
@desc:
'''
import os,sys,re,glob
import pandas as pd
import argparse
from subprocess import call
import datetime
from daemon.daemon import Daemon
import panel_return as pr

reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("/biocluster/data/biobk/user_test/zhaohongqiang/software/miniconda2/lib/python2.7/site-packages")
from apscheduler.schedulers.blocking import BlockingScheduler



MODES = {"sc", "FP","DP",}
main_parser = argparse.ArgumentParser(description=u"RUN 分析流程",
                                      formatter_class=argparse.ArgumentDefaultsHelpFormatter)

mode_parser = main_parser.add_argument_group("Mode input options")
mode_parser.add_argument("mode", metavar="Mode",
                         help="Mode to run the pipleine for. Choose from %s" % list(MODES), choices=MODES)

args = main_parser.parse_args(sys.argv[1:2])
mode = args.mode

parser = argparse.ArgumentParser(description="Run Pipeline in %s mode" % mode, prog=" ".join(sys.argv[0:2]),
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

general_parser = parser.add_argument_group("General input options")
general_parser.add_argument("mode", metavar=mode,
                            choices=MODES)

if mode == "sc":
    screen_parser = parser.add_argument_group("screen options")
    screen_parser.add_argument("-px", dest="project_xls", help=u"输入project 地址",default="/hongshan/software/zuzhi/script/project_record/zhaohongqiang/project_record-zhaohongqiang.xlsx")
    screen_parser.add_argument("-time",dest="time",help=u"当日分析时间",default=datetime.datetime.strftime(datetime.datetime.now(),"%Y.%m.%d"))
    screen_parser.add_argument("-snv",action='store_false',help=u"输入 snv 即关闭 snv截图")
    screen_parser.add_argument("-cnv", action='store_false',help=u"输入 cnv 即关闭 cnv截图")
    screen_parser.add_argument("-sv", action='store_false',help=u"输入 sv 即关闭 sv截图")
    screen_parser.add_argument("-u",dest="user",default="/biocluster/data/biobk/user_test/zhaohongqiang/sample",help=u"check文件保存目录")
    screen_parser.add_argument("-timing",action='store_false',help=u"关闭计时器")
elif mode == "FP":
    FP_parser = parser.add_argument_group("False positive options")
    FP_parser.add_argument("-xls",dest="xls",help="input xls file")
    FP_parser.add_argument("-d",dest="false_dir")
elif mode == "DP":
    DP_parser= parser.add_argument_group(u"低频截图 options")
    DP_parser.add_argument("-p",dest="project")
    DP_parser.add_argument("-xls",dest="xls")

args = parser.parse_args()

def screen_job():
    '''
    sc 主要的功能为检测 样本记录时间内的样本然后监控是否下机，每小时检测一次，下机后自动运行snv cnv sv截图
    search project count with run screenshot to project
    args input snv close snv
    args input cnv close cnv
    args input sv close sv
    :return:
    '''


    project_df = pd.read_excel(args.project_xls)
    # project_df.loc["2020.5.15", [u"项目 panel", u"样本名称T"]]
    f = open(os.path.join(args.user,args.time,"check.temp.txt"), "a")
    for pro, T_sample in zip(project_df[u"项目 panel"][args.time], project_df[u"样本名称T"][args.time]):
        print (pro, T_sample)
        if pro in pr.panel_dic.keys():
            pro=pr.turn_panel(pro)
            print (pro, T_sample)

            try:
                project = glob.glob("/clinical/public/{pro}/*{T_sample}*".format(pro=pro, T_sample=T_sample))[0]
                print(project)
            except:
                continue


            if os.path.exists(project+"/03_report/qc_report/report.sh")and oct(os.stat(project+"/03_report/qc_report/report.sh").st_mode)[-3:] =="777" and os.path.exists(project+"/sv.igv.o")==False:
                os.chdir(project)
                for i in os.popen("/hongshan/software/zuzhi/script/check/check.sh"):
                    f.write(i)

                cmd = "sh /biocluster/data/biobk/user_test/yanyali/optimize/jietu/pair/snapshot_pair.sh"
                if args.sv:
                    call('xvfb-run --auto-servernum sh /hongshan/software/zuzhi/script/sv/newsvigv/sv.igv_new.sh  >sv.igv.o 2>&1  ',shell=True)
                # if args.snv:
                #     call(cmd,shell=True)#,shell=True
                os.chdir(project+'/03_report/qc_report')
                # if args.cnv:
                #     call("sh /hongshan/software/zuzhi/script/cnv/cnv_confirm/cnv_result.sh > cnv_auto_result.txt",shell=True)
                # if args.sv:
                    # call("nohup xvfb-run --auto-servernum sh /hongshan/software/zuzhi/script/sv/svigv/sv.igv.sh >sv.igv.o 2>&1 & ",shell=True)#

                f.write("#" * 100 + "\n\n")


    f.close()
    now = datetime.datetime.now()
    today8am = now.replace(day=int(args.time.split(".")[-1]), hour=8, minute=0, second=0, microsecond=0)
    if now > today8am:
        os._exit(0)
    else:
        pass


def DP_job():
    '''
    低频截图 输入文件名即可截图
    :return:
    '''
    print(args.project)
    print(args.xls)
    xls=args.xls
    Tbam=glob.glob(args.project+"/01_aln/*T_recal.bam")[0]
    Nbam=glob.glob(args.project+"/01_aln/*N_recal.bam")[0]
    Tname=args.project.split("/")[-1].split("_")[1]
    os.system("mkdir -p igv_low/igv/snv")
    os.system("python /biocluster/data/biobk/user_test/yanyali/optimize/jietu/pair/mutVision.py\
      --mutF {xls}\
      --bam {Tbam} \
      --id {Tname} \
      --outdir igv_low/igv \
      --nbam {Nbam} \
      --num_reads 10 \
      --nNum_reads 50 \
      --nvNum_reads 50 \
      --vNum_reads 120".format(**locals()))



def FP_job():
    def read_summary(summary_xls,freq,alt_depth):
        fs = open(summary_xls).read()
        p = re.compile('#', re.S)
        p.split(fs)[1].split("\n")
        result_freq=0
        result_alt_depth=0
        for i in p.split(fs)[1].split("\n"):
            if i.split("\t")[0] == freq:
                if float(i.split("\t")[2])<0.1:
                    result_freq=1
                else:
                    result_freq=0
        for i in p.split(fs)[2].split("\n"):
            if i.split("\t")[0] == alt_depth:
                if float(i.split("\t")[2])<0.1:
                    result_alt_depth=1
                else:
                    result_alt_depth=0
        if result_alt_depth+result_freq ==2:
            return True
        else:
            return False

    gene_chr_pos=[]

    def fillter(x):
        #     print x["Tumor_mutant_frequency"]
        freq = x["Tumor_mutant_frequency"]
        alt_depth = x["talt_depth"]
        return read_summary(i, freq, alt_depth)



    df = pd.read_table(args.xls)
    for i in glob.glob(args.false_dir+"/*summary.xls"):

        print i
        gene_pos = re.findall("_{1}([A-Za-z0-9]+_[0-9XY]+_\d+_)", os.path.basename(i))[0].split("_")
        Gene_Name=gene_pos[0]
        Start_position = gene_pos[2]
        # print df.query('Gene_Name==@Gene_Name and Start_position==@Start_position'),Start_position
        result = df.query('Gene_Name==@gene_pos[0] and Start_position==@gene_pos[2]')
        # print result
        if result.apply(fillter, axis=1).values[0]:
            pass


        else:
            df = df.query('Gene_Name!=@gene_pos[0] and Start_position!=@gene_pos[2]')

    df.to_csv(os.path.basename(args.xls)+"_drop.xls",index=False,sep="\t")

if __name__ == '__main__':
    if args.mode =="sc":
        print args
        if args.timing:

            if os.path.exists(os.path.join(args.user,args.time,"check.temp.txt")):

                pass
            else:
                os.mkdir(os.path.join(args.user,args.time))
                f = open(os.path.join(args.user,args.time,"check.temp.txt"), "w")
                f.close()
            scheduler = BlockingScheduler()
            scheduler.add_job(screen_job, 'interval',  hours=1)
            scheduler.start()
        else:
            if os.path.exists(os.path.join(args.user, args.time, "check.temp.txt")):

                pass
            else:
                os.mkdir(os.path.join(args.user, args.time))
                f = open(os.path.join(args.user, args.time, "check.temp.txt"), "w")
                f.close()
            screen_job()

        # screen_job()
    if args.mode == "FP":
        FP_job()
    if args.mode == "DP":
        DP_job()