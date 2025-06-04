# server_backup
解析サーバーからバックアップサーバーに解析データをコピー(upload)、またはバックアップしたデータを解析サーバにコピー(download)する。

## 変数の定義(共通)
```
img=/data1/labTools/labTools.sif
SCRIPT=/data1/labTools/server_backup/latest/server_backup.py
```
マニュアルの表示（全体）
```
$ singularity exec --disable-cache --bind /data1 $img python $SCRIPT --help
usage: server_backup.py [-h] [--version] {upload,up,download,dl} ...

upload/download to/from backup server.

positional arguments:
  {upload,up,download,dl}
    upload (up)         Upload to backup server.
    download (dl)       Download from backup server.

optional arguments:
  -h, --help            show this help message and exit
  --version, -v         show program's version number and exit
```
コマンド別の詳細表示
```
singularity exec --disable-cache --bind /data1 $img python $SCRIPT <command> --help
```
| command     | 概要                                                |
|:------------|:---------------------------------------------------|
|upload, up   ||
|download, dl ||

# 1\. データのバックアップ（アップロード）
解析時に作成されたデータを /data2 にマウントされたバックアップサーバーにコピーする。
## オプションの詳細
```
$ singularity exec --disable-cache --bind /data1 $img python $SCRIPT up --help
usage: server_backup.py upload [-h] --flowcellid FLOWCELLID [--project_type {both,WTS,eWES}] [--inclusion INCLUSION] [--exclusion EXCLUSION]
                               [--directory DIRECTORY] [--forwarding FORWARDING]

optional arguments:
  -h, --help            show this help message and exit
  --flowcellid FLOWCELLID, -fc FLOWCELLID
                        flowcell id (default: None)
  --project_type {both,WTS,eWES}, -t {both,WTS,eWES}
                        project type (default: both)
  --inclusion INCLUSION, -i INCLUSION
                        sample IDs to include (comma separated) (default: )
  --exclusion EXCLUSION, -e EXCLUSION
                        sample IDs to exclude (comma separated) (default: )
  --directory DIRECTORY, -d DIRECTORY
                        parent analytical directory (default: /data1/data/result)
  --forwarding FORWARDING, -fw FORWARDING
                        forwarding directory path (default: /data2/backup/result)
```
| option           | 概要           |default         |
|:-----------------|:---------------|:---------------|
|--flowcellid/-fc  |バッチ固有のID。OncoStationに掲載されている9桁の半角英数字  |None |
|--project_type/-t |解析種別。bath,eWES,WTSから選択する |both                   |
|--inclusion/-i    |アップロードするSample IDを指定。カンマ区切りで複数指定可能 |None |
|--exclusion/-e    |除外するSample IDを指定。カンマ区切りで複数指定可能         |None |
|--directory/-d    |解析フォルダの親ディレクトリ        |/data1/data/result     |
|--forwarding/-fw  |バックアップ先のディレクトリパス　　|/data2/backup/result   |

