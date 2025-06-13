import os
import sys
import datetime
import pandas as pd
from pathlib import Path
from .subfunc import *

tempDir = Path(os.path.abspath(__file__)).parent.parent / "tmp"
os.makedirs(tempDir, exist_ok=True)

def copyfiles(files, forward, chsfile, tempDir) :
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
    mvCmd = f"mv -f {ckspath} {forward}/checksum && rsync -avzru {chsfile} checksum.origin && "
    endCmd = f"rm -f {listpath}"
    cmd = copyCmd + chkCmd + mvCmd + endCmd

    qsubCmd = f"/data1/apps/sge/bin/lx-amd64/qsub -N BK_{time_str} -q all.q -pe smp 2 -o /dev/null -e /dev/null << EOF\n{cmd}\nEOF"
    os.system(qsubCmd)
    os.system("sleep 0.1")

def run_download(args):

    sampleID = args.sample
    listfile = args.listfile
    directory = args.directory
    forwarding = args.forwarding

    if listfile is None :
        if sampleID is None :
            init('Incorrect argument specified.')
        else :
            sampleID = [x.strip() for x in sampleID.split(',') if not x.strip() == '']
    elif not os.path.isfile(listfile) :
        init('List file does not exist.')
    else :
        with open(listfile, 'r') as f:
            try:
                sampleID = f.read().splitlines()
            except FileNotFoundError as e:
                init(e)

    sampleID = rmdup_list(sampleID)

    df_info = getinfo()
    if df_info.shape[0] == 0 : init("No matching data found.")

    not_exists = list(set(sampleID) - set(df_info['SAMPLE_ID']))
    if len(not_exists) > 0:
        init('The following samples have not been uploaded to backup server.\n' + '\n'.join(not_exists))

    df_info = df_info[ df_info['SAMPLE_ID'].isin(sampleID) ]
    if df_info.shape[0] == 0 : init("No matching data found.")

    df_info['PRJ_TYPE'] = df_info['PRJ_TYPE'].str.replace('EWES',"eWES")

    for i, item in df_info.iterrows() :
        fcDir = SearchDir(item['sub_name'], Path(forwarding + '/' + item['PRJ_TYPE']))
        rawDir = os.path.join(forwarding, item['PRJ_TYPE'], fcDir, item['SAMPLE_ID'])
        forDir = os.path.join(directory, item['PRJ_TYPE'], fcDir, item['SAMPLE_ID'])
        chsfile = os.path.join(rawDir,'checksum')
        if not os.path.isfile(chsfile):
            print('Backup data is incorrect: ' + item['SAMPLE_ID'])
            continue

        # FASTQ
        FILES_FQ = [ os.path.join(rawDir,file) for file in Path(rawDir).iterdir() if file.name.endswith('fastq.gz') ]

        # report, summarized
        FILES_SUM = [ os.path.join(rawDir,file) for file in Path(rawDir).iterdir() if 'summarized' in file.name ]
        FILES_REP = [ os.path.join(rawDir,file) for file in Path(rawDir).iterdir() if 'report' in file.name ]

        if item['PRJ_TYPE'] == 'eWES':
            FILE_BAM = os.path.join(rawDir, '.'.join([item['SAMPLE_ID'],'tumour','aligned','bam']))
            FILE_VCF = os.path.join(rawDir, item['SAMPLE_ID']+'_mutect2_freebayes_lofreq_vote_res.exome.vcf')
            copyfiles(FILES_FQ + FILES_SUM + FILES_REP + [FILE_BAM, FILE_VCF], forDir, chsfile, tempDir)

        elif item['PRJ_TYPE'] == 'WTS':
            FILE_BAM = os.path.join(rawDir, '.'.join([item['SAMPLE_ID'],'Aligned','sortedByCoord','out','bam']))
            copyfiles(FILES_FQ + FILES_SUM + FILES_REP + [FILE_BAM], forDir, chsfile, tempDir)


