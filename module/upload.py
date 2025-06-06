import os
import sys
import argparse
import pandas as pd
import datetime
from pathlib import Path
from .common import *

tempDir = Path(os.path.abspath(__file__)).parent.parent / "tmp"
os.makedirs(tempDir, exist_ok=True)

def sendfiles(files, forward: Path, tempDir) :
    now = datetime.datetime.now()
    time_str = now.strftime("%d%H%M%S") + str(now.microsecond)
    listpath = os.path.join(tempDir, f".{time_str}.list")
    ckspath = os.path.join(tempDir, f".{time_str}.cks")
    f = open(listpath, 'w')
    f.write('\n'.join(files))
    f.close()

    os.makedirs(forward, exist_ok=True, mode=0o777)
    copyCmd = f"rsync -azruL --no-relative --files-from={listpath} / {forward}/ && "
    chkCmd = f"cd  {forward}/ && if [ -s \"checksum\" ]; then rm checksum; fi && md5sum ./* > {ckspath} && "
    mvCmd = f"mv -f {ckspath} {forward}/checksum && "
    endCmd = f"rm -f {listpath} {ckspath}"
    cmd = copyCmd + chkCmd + mvCmd + endCmd

    qsubCmd = f"/data1/apps/sge/bin/lx-amd64/qsub -N BK_{time_str} -q all.q -pe smp 2 -o /dev/null -e /dev/null << EOF\n{cmd}\nEOF"
    os.system(qsubCmd)
    os.system("sleep 0.1")

def run_upload(args):

    flowcellid = args.flowcellid
    directory = args.directory
    project_type = args.project_type
    forwarding = args.forwarding
    inclusion = [x.strip() for x in args.inclusion.split(',') if not x.strip() == '']
    exclusion = [x.strip() for x in args.exclusion.split(',') if not x.strip() == '']

    if len(inclusion) > 0 and len(exclusion) > 0:
        init('ERROR: Inclusion and exclusion cannot be specified simultaneously.')

    df_info = getinfo(flowcellid)
    if df_info.shape[0] == 0 : init("No matching data found.")

    if len(inclusion) > 0:
        print ("inclusion sample:" + "\n".join(inclusion))
        df_info = df_info[ df_info['SAMPLE_ID'].isin(inclusion) ]
        if df_info.shape[0] == 0 : init("No corresponding sample IDs.")

    if len(exclusion) > 0:
        print ("exclusion sample:" + "\n".join(exclusion))
        df_info = df_info[ ~df_info['SAMPLE_ID'].isin(exclusion) ]
        if df_info.shape[0] == 0 : init("No corresponding sample IDs.")

    if project_type == "both" :
        TYPES = ['eWES','WTS']
    else :
        TYPES = [project_type]

    df_info['PRJ_TYPE'] = df_info['PRJ_TYPE'].str.replace('EWES',"eWES")
    df_info = df_info[ df_info['PRJ_TYPE'].isin(TYPES) ]
    if df_info.shape[0] == 0 : init("Test type error: no sample ID corresponds.")

    df_info = df_info.sort_values('SAMPLE_ID')
    for i, item in df_info.iterrows() :

        while True :
            fcDir = SearchDir(item['sub_name'], Path(directory + '/' + item['PRJ_TYPE']))
            if fcDir is None : init('Analysis folder not found.')
            rawDir = os.path.join(directory, item['PRJ_TYPE'], fcDir, item['SAMPLE_ID'])
            forDir = os.path.join(forwarding, item['PRJ_TYPE'], fcDir, item['SAMPLE_ID'])

            # FASTQ
            if not os.path.isdir(os.path.join(rawDir,'Fastq')) :
                print('Fastq folder does not exist. Cancel transfer.: ' + item['SAMPLE_ID'])
                break

            FILES_FQ = [ os.path.join(rawDir,'Fastq',file) for file in Path(os.path.join(rawDir,'Fastq')).iterdir() if file.name.endswith('fastq.gz') ]

            # report, summarized
            if not os.path.isdir(os.path.join(rawDir,'Summary')) :
                print('Summary folder does not exist. Cancel transfer.: ' + item['SAMPLE_ID'])
                break

            FILES_SUM = [ os.path.join(rawDir,'Summary',file) for file in Path(os.path.join(rawDir,'Summary')).iterdir() if 'summarized' in file.name ]
            FILES_REP = [ os.path.join(rawDir,'Summary',item['SAMPLE_ID'] + '.report.'+file) for file in ['pdf','json'] ]

            if item['PRJ_TYPE'] == 'eWES':
                if not os.path.isdir(os.path.join(rawDir,'Preprocessing','align')) :
                    print('align folder does not exist. Cancel transfer.: ' + item['SAMPLE_ID'])
                    break

                FILE_BAM = os.path.join(rawDir,'Preprocessing','align','.'.join([item['SAMPLE_ID'],'tumour','aligned','bam']))

                if not os.path.isdir(os.path.join(rawDir,'SNV','somatic')) :
                    print('SNV folder does not exist. Cancel transfer.: ' + item['SAMPLE_ID'])
                    break

                FILE_VCF = os.path.join(rawDir,'SNV','somatic',item['SAMPLE_ID']+'_mutect2_freebayes_lofreq_vote_res.exome.vcf')

                sendfiles(FILES_FQ + FILES_SUM + FILES_REP + [FILE_BAM, FILE_VCF], forDir, tempDir)

            elif item['PRJ_TYPE'] == 'WTS':
                if not os.path.isdir(os.path.join(rawDir,'Expression','STAR_align_exp')) :
                    print('align folder does not exist. Cancel transfer.: ' + item['SAMPLE_ID'])
                    break

                FILE_BAM = os.path.join(rawDir,'Expression','STAR_align_exp','.'.join([item['SAMPLE_ID'],'Aligned','sortedByCoord','out','bam']))

                sendfiles(FILES_FQ + FILES_SUM + FILES_REP + [FILE_BAM], forDir, tempDir)


