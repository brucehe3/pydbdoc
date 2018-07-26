pydbdoc
===================

1. 从MySQL数据库读取表信息并转为markdown文档

2. 支持生成png格式的关系图

Author: Bruce He <bruce@shbewell.com>

Version: `0.2`

Requirements
-------------
* Python(2.7,3.4,3.5,3.6)
* pymysql
* pygraphviz

Installation
------------

本工具使用 `pymysql` 作为连接数据库的适配器，请先

```bash
pip install pymysql

```




Documentation
-------------

### 使用方式
```
usage: pydbdoc.py [-h] [--host HOST] [--user USER] [--name NAME] [-p]
                  [--gitlab] [--graph] [-f] [--migration MIGRATION]
                  [dest]

DB自文档化助手 0.2

positional arguments:
  dest                  指定生成的文件地址 如：app/db.md

optional arguments:
  -h, --help            show this help message and exit
  --host HOST           数据库地址
  --user USER           数据库用户名
  --name NAME           数据库名称
  -p, --password        使用数据库密码
  --gitlab              支持gitlab的样式
  --graph               导出png图片格式
  -f, --force           是否覆盖存在的md文件
  --migration MIGRATION
                        指定migration目录


```


从本地`test`数据库导出数据表结构及信息

```
python pydbdoc.py db.md --name test -p

```

从本地`test`数据库导出为表关系图

```
python pydbdoc.py db.png --name test -p --graph

```


#### 输出的MD文档

见 [md.md][demo]

[demo]: https://github.com/brucehe3/pydbdoc/blob/master/db.md