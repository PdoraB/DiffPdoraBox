#-*- coding:utf-8 -*-
#/usr/bin/env python

'''
This script will load IGV in a virtual X window, load all supplied input files
as tracks, and take snapshots at the coorindates listed in the BED formatted
region file.

If you don't have a copy of IGV, get it here:
http://data.broadinstitute.org/igv/projects/downloads/IGV_2.3.81.zip

example IGV batch script:

new
snapshotDirectory IGV_Snapshots
load test_alignments.bam
genome hg19
maxPanelHeight 500
goto chr1:713167-714758
snapshot chr1_713167_714758_h500.png
goto chr1:713500-714900
snapshot chr1_713500_714900_h500.png
exit
'''
import pandas as pd
import argparse
import os,glob,sys

parser = argparse.ArgumentParser()
parser.add_argument('-input',dest='input_file',help=u'输入文件名必须包含chr pos ')
parser.add_argument('-o',dest='output_dir',help=u'输出目录')
parser.add_argument('-T',dest='tumor_bam',help=u'tumor_bam')
parser.add_argument('-N',dest='normal_bam',help=u'normal_bam')
parser.add_argument('--bedtools',dest='bedtools_path',default='/gpfs1/RD_project/software/RD_software/bedtools_2.28/bin/bedToIgv')
parser.add_argument('--igv',dest='igv_path',default='/gpfs1/RD_project/software/RD_software/igv/bin/igv')
args=parser.parse_args()
def mutation_to_bed(input_file,outbed_file):  ## bed读取
    '''

    :param input_file:
    :param outbed_file:
    :return: result bed
    '''
    if input_file.endswith("xls"):
        data_mut = pd.read_excel(input_file)
    elif input_file.endswith("csv"):
        data_mut = pd.read_csv(input_file)
    else:
        data_mut = pd.read_table(input_file)
    data_anno = data_mut[['GENE','AA_Mutation','chr','pos','ref','alt']]
    def start_end(x):
        start = int(x['pos']) - 20
        end = int(x['pos']) + 20
        return start,end
    data_anno=data_anno[~data_anno['pos'].isnull()]
    data_anno['start'],data_anno['end'] = zip(*data_anno[~data_anno['pos'].isnull()].apply(start_end,axis=1))
    data_anno[['chr','start','end']].to_csv(outbed_file,sep='\t',index=False,header=False)
    return outbed_file

def run_igv_snapshots(bed):
    '''

    :param bed:
    :return: run igv
    '''
    
    bam_tumor = args.tumor_bam
    bam_normal = args.normal_bam
    fasta = '/gpfs1/software/pipeline/pipeline/database/ref/hg19/hg19.fasta'  #fasta文件
    os.system('python make_IGV_snapshots.py {bam_tumor} {bam_normal} -ht 1200 -g {fasta} -r {bed}'.format(**locals()))
    

name= args.input_file
bed = mutation_to_bed(args.input_file,args.output_dir+'/{name}_IGV.bed'.format(**locals()))
