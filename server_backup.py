import os
import sys
import argparse
import pymysql
import pandas as pd
import datetime
import warnings
from pathlib import Path
from module import *

tempDir = os.path.join(os.path.dirname(__file__), 'tmp')
os.makedirs(tempDir, exist_ok=True)

def main():

    parser = argparse.ArgumentParser(
        description="upload/download to/from backup server."
    )
    parser.add_argument('--version','-v', action='version', version='%(prog)s v2.0.0')
    subparsers = parser.add_subparsers(dest="command", required=True)

    # upload
    parser_ul = subparsers.add_parser("upload", aliases=['up'], help="Upload to backup server.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_ul.add_argument("--flowcellid","-fc", required=True, help="flowcell id")
    parser_ul.add_argument("--project_type","-t", required=False, help="project type", default="both", choices=["both","WTS","eWES"])
    parser_ul.add_argument("--inclusion","-i", required=False, help="sample IDs to include (comma separated)", default="")
    parser_ul.add_argument("--exclusion","-e", required=False, help="sample IDs to exclude (comma separated)", default="")
    parser_ul.add_argument("--directory","-d", required=False, help="parent analytical directory", default="/data1/data/result")
    parser_ul.add_argument("--forwarding","-fw", required=False, help="forwarding directory path", default="/data2/backup/result")
    parser_ul.set_defaults(func=run_upload)

    # download
    parser_dl = subparsers.add_parser("download", aliases=['dl'], help="Download from backup server.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_dl.add_argument("--sample","-s", required=False, help='sample IDs to download (comma separated)')
    parser_dl.add_argument("--listfile","-f", required=False, help="List of samples to be download.")
    parser_dl.add_argument("--directory","-d", required=False, help="output directory", default="/data1/work/backup_storage")
    parser_dl.add_argument("--forwarding","-fw", required=False, help="forwarding directory path", default="/data2/backup/result")
    parser_dl.set_defaults(func=run_download)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":

    main()



