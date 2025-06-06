import os
import sys
import pymysql
import pandas as pd
import warnings
from pathlib import Path

def getinfo(fc_id=""):

    try:
        connection = pymysql.connect(host="192.168.9.100", user="gxd_pipeline", password="gw!2341234", database="gxd")
    except Exception as e:
        sys.exit({e})

    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        db_tbl = pd.read_sql(SelectData(fc_id), connection)
        db_tbl.drop_duplicates()

    return db_tbl


def SelectData(fc_id=""):

    query = f"""
    SELECT tesh.run_id, concat(tesh.equip_side, tesh.fc_id) AS sub_name, gp.PRJ_TYPE, ghl.ANAL_STATUS, gp.SAMPLE_ID
    FROM gxd.tb_expr_seq_header tesh
    INNER JOIN gxd.gc_qc_sample gqs
    ON tesh.run_id = gqs.run_id
    INNER JOIN gxd.gc_project gp
    ON gqs.SAMPLE_ID = gp.SAMPLE_ID
    INNER JOIN gxd.gc_history_log ghl
    ON gqs.SAMPLE_ID = ghl.SAMPLE_ID
    AND ghl.idx = (SELECT MAX(idx) FROM gc_history_log WHERE SAMPLE_ID = gqs.SAMPLE_ID)
    """
    if fc_id != "" :
        query += f"WHERE tesh.fc_id = '{fc_id}'"

    return query

def SearchDir(batchID, forwarding : Path):
    fcDirs = [fcDir for fcDir in forwarding.iterdir() if fcDir.name.endswith(batchID)]
    fcDirs.sort()
    if len(fcDirs) != 1: return None
    return os.path.basename(fcDirs[-1])

def init(msg):
    print(msg)
    sys.exit(1)


