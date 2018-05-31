pydbdoc
===================

从MySQL数据库读取表信息并转为markdown文档

Author: Bruce He <bruce@shbewell.com>

Version: `0.1`

Requirements
-------------
* Python(2.7,3.4,3.5,3.6)
* pymysql

Installation
------------

本工具使用 `pymysql` 作为连接数据库的适配器，请先

```bash
pip install pymysql

```


将 `pydbdoc.py` 直接下载到相应代码目录下

Documentation
-------------

### 使用方式
```
usage: pydbdoc.py [-h] [--host HOST] [--user USER] [--name NAME] [-p] [-f]
                  [dest]

DB自文档化助手 0.1

positional arguments:
  dest            指定生成的文件地址 如：app/db.md

optional arguments:
  -h, --help      show this help message and exit
  --host HOST     数据库地址
  --user USER     数据库用户名
  --name NAME     数据库名称
  -p, --password  使用数据库密码
  -f, --force     是否覆盖存在的md文件

```


从本地`test`数据库导出数据表结构及信息

```
python pydbdoc.py db.md --name test -p

```


#### 输出的MD文档

见 [md.md][demo]

[demo]: https://github.com/brucehe3/pydbdoc/blob/master/db.md