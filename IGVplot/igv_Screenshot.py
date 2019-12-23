#-*- coding:utf-8 -*-
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
def mutation_to_bed(input_file,outbed_file):
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
    
    bam_tumor = args.tumor_bam
    bam_normal = args.normal_bam
    fasta = '/gpfs1/software/pipeline/pipeline/database/ref/hg19/hg19.fasta'
    os.system('python make_IGV_snapshots.py {bam_tumor} {bam_normal} -ht 1200 -g {fasta} -r {bed}'.format(**locals()))
    

name= args.input_file.split('/')[-1].split('.')[0]
bed = mutation_to_bed(args.input_file,args.output_dir+'/{name}_IGV.bed'.format(**locals()))
