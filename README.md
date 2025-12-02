# server_backup
CAP storageからbackup storageに解析データをコピー(upload)、またはバックアップしたデータをCAP storageにコピー(download)する。\
指定された sample ID や flowcell ID から検体情報をデータベースに問い合せ、CAP storage/backup storage内のファイルを検索して転送します。そのためデータベースに登録がない検体や、規程の場所に中間ファイルがない検体に対しては実行できません。\
**データベースの設計内容が不明なため、データベース検索時に想定外の動作を行う可能性があります。**\
**このツールは正式な検証を経ていません。** 不具合等が生じた場合は適宜修正するか、[backup storageへ転送されるデータ](https://github.com/mkaba-gxd/server_backup/tree/v2.0.0?tab=readme-ov-file#転送されるデータ)または[backup storageから復帰させるデータ](https://github.com/mkaba-gxd/server_backup/tree/v2.0.0?tab=readme-ov-file#転送されるデータ-1)を参照して該当データを手動でrsync転送してください。

| command          | 概要                                                     |
|:-----------------|:---------------------------------------------------------|
|[upload, up](#UP)   |CAP storageからbackup storageに解析データをコピーする |
|[download, dl](#DL) |バックアップしたデータをCAP storageサーバにコピーする      |

## エイリアスの作成 ※ 初回のみ
~/bin フォルダ直下に以下のコマンドを記載したテキストファイル worksheet を作成し、実行権限を付与する。
エイリアスを作成しない場合は、singularity でコンテナとスクリプトファイルを指定して実行する。
（gxd_pipeline, guest_user ユーザーには実装済み）
```
singularity exec --disable-cache --bind /data1 --bind /data2 /data1/labTools/labTools.sif python /data1/labTools/server_backup/latest/server_backup.py $@
```
helpページを表示してエイリアスの設定を確認する。以下が表示されればOK。
```
$ server_backup -h
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
server_backup <command> --help
```
<a id="UP"></a>
## 1\. データのバックアップ（アップロード）
解析時に作成されたデータをbackup storageにコピーし、チェックサムを作成する。
```
server_backup upload --flowcellid <flowcellid>
server_backup up -fc <flowcellid>
```
### 転送されるデータ
**【eWES】**
<img src="https://github.com/user-attachments/assets/ecc3234c-697f-40ed-94b2-be9ffd26a245" width="1000">

**【WTS】**
<img src="https://github.com/user-attachments/assets/8a44e398-ef35-470d-8eca-f4e920f1f760" width="1000"> \
※ レポートの修正を行った場合、修正前後の \<sampleID\>.summarized.*.tsv ファイルが転送される。\
※ 転送するデータが1つでも足りない場合、当該検体はスキップする。\
※ ANAL_STATUSが102以外の検体が含まれていた場合、作業続行するかどうか聞かれる。Yesを選択すると当該検体を除いて転送作業を続行し、Noを選択すると終了する。

### オプションの詳細
```
$ server_backup up --help
usage: server_backup.py upload [-h] --flowcellid FLOWCELLID [--project_type {both,WTS,eWES}] [--inclusion INCLUSION] 
                               [--exclusion EXCLUSION] [--directory DIRECTORY] [--forwarding FORWARDING] [--preparation]
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
  --preparation, -p     Only transfer large files (default: False)
```
| option           |required | 概要           |default            |
|:-----------------|:-------:|:---------------|:------------------|
|--flowcellid/-fc  |True     |バッチ固有のID。OncoStationに掲載されている9桁の半角英数字  |None |
|--project_type/-t |False    |解析種別。bath,eWES,WTSから選択する |both                   |
|--inclusion/-i    |False    |アップロードするSample IDを指定。カンマ区切りで複数指定可能 |None |
|--exclusion/-e    |False    |除外するSample IDを指定。カンマ区切りで複数指定可能         |None |
|--directory/-d    |False    |解析フォルダの親ディレクトリ        |/data1/data/result     |
|--forwarding/-fw  |False    |バックアップ先のディレクトリパス　　|/data2/backup/result   |
|--preparation/-p  |False    |大きいデータ(fastq.gz,bam,vcf)の転送のみ実行 | False        |

<a id="DL"></a>
## 2\. バックアップデータの復帰（ダウンロード）
backup storageに保存したデータをCAP storageにコピーし、チェックサムを作成するジョブが投入される。
```
server_backup download --sample <samples>
server_backup dl -s <samples>
```
または
```
server_backup download --listfile <sample listfile path>
server_backup dl -f <sample listfile path>
```
### 転送されるデータ
**【eWES】**
<img src="https://github.com/user-attachments/assets/988a6b31-d815-4a98-9f0e-06c662997aba" width="1000">

**【WTS】**
<img src="https://github.com/user-attachments/assets/6bffbd1d-6b5c-496b-bc07-19c167a7f27b" width="1000"> 
### オプションの詳細
```
$ server_backup download --help
usage: server_backup.py download [-h] [--sample SAMPLE] [--listfile LISTFILE]
                                 [--directory DIRECTORY] [--forwarding FORWARDING]
optional arguments:
  -h, --help            show this help message and exit
  --sample SAMPLE, -s SAMPLE
                        sample IDs to download (comma separated) (default: None)
  --listfile LISTFILE, -f LISTFILE
                        List of samples to be download. (default: None)
  --directory DIRECTORY, -d DIRECTORY
                        output directory (default: /data1/work/backup_storage)
  --forwarding FORWARDING, -fw FORWARDING
                        forwarding directory path (default: /data2/backup/result)
```
| option          |required | 概要                               |default                    |
|:----------------|:-------:|:-----------------------------------|:--------------------------|
|--sample/-s      |False*   |Sample ID。カンマ区切りで複数指定可能 |None                       |
|--listfile/-f    |False*   |downloadするSample IDリストのファイルパス。<br>Sample IDを1列に記載する |None |
|--directory/-d   |False    |データを復帰させる場所               |/data1/work/backup_storage |
|--forwarding/-fw |False    |バックアップ先のディレクトリパス      |/data2/backup/result       |

***--sample または --listfile のいずれか1つを指定する。**
