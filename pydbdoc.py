#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
读取数据库中的信息生成markdown文档
===========================================================================
@Author Bruce He <hebin@comteck.cn>
@Date  2018-07-26
@Version 0.2
"""
import os
import re
import argparse
import pymysql
import getpass
from collections import namedtuple
from lib.generator import MDGenerator, GraghGenerator


Column = namedtuple('Column', ['name', 'field_type', 'collation', 'if_null', 'key', 'default', 'extra', 'privileges',
                               'comment', ])

TableInfo = namedtuple('TableInfo', ['name', 'engine', 'version', 'row_format', 'rows', 'avg_row_length',
                                     'data_length', 'max_data_length', 'index_length', 'data_free', 'auto_increment',
                                     'create_time', 'update_time',
                                     'check_time', 'collation', 'checksum', 'create_options', 'comment'])


class DB:
    def __init__(self, host='localhost', user='root', password='', name='test', charset='utf8mb4'):
        self.connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            db=name,
            charset=charset
        )

        self.cursor = self.connection.cursor()
        self.md_generator = MDGenerator()
        self.graph_generator = GraghGenerator()
        self.migration_tables = {}

    def sync_from_migration(self, migration_path):
        """
        从migration同步  table comment
        :return:
        """
        if not os.path.exists(migration_path):
            raise AttributeError('The path is not found.')

        if not os.path.isdir(migration_path):
            raise AttributeError('The path should be a folder.')

        migration_files = []
        for dirpath, dirname, filenames in os.walk(migration_path):
            for filename in filenames:
                # 只读取php文件
                if filename[-4:].lower() == '.php':
                    migration_files.append(os.path.join(dirpath, filename))

        # 读取并分析代码
        self.find_comment_from_migration(migration_files)

    def find_comment_from_migration(self, migration_files):
        """
        寻找特征注释文档
        :return:
        """
        if not migration_files:
            raise AttributeError('No need files to process.')

        pattern = re.compile("Schema\:\:create\((.*?),[\s\S]*?\$table\->comment([\s\S]*?)\;")

        # 读取文件找到所有符合的注释
        for doc_name in migration_files:
            with open(doc_name) as f:
                try:
                    php_content = f.read()
                    results = pattern.findall(php_content)
                    if results:
                        self.split_table_comment(results)
                except UnicodeDecodeError:
                    pass
                    # print(doc_name, '编码有误，跳过...')
                except AttributeError as e:
                    print(doc_name, str(e))

    def split_table_comment(self, results):
        """
        切分表名和表注释
        :param results:
        :return:
        """
        for result in results:
            table_name = result[0].strip(" '")
            table_comment = result[1].strip(" '=")
            self.migration_tables[table_name] = table_comment

    def get_tables(self):
        """
        return table list
        :return:
        """
        self.cursor.execute("SHOW TABLES;")
        return self.cursor.fetchall()

    def get_columns(self, table):
        """
        return columns data from table
        :param table:
        :return:
        """
        self.cursor.execute("SHOW FULL COLUMNS FROM %s;" % table)
        columns = self.cursor.fetchall()
        return self.wrap_columns(columns)

    def wrap_columns(self, columns):
        return [Column._make(column) for column in columns]

    def get_table_info(self, table_name):

        self.cursor.execute("SHOW TABLE STATUS WHERE name=%s ", table_name)
        return TableInfo._make(self.cursor.fetchone())

    def init_path(self, dest, override):
        """
        路径初始化
        :param dest:
        :param override:
        :return:
        """
        if not override and os.path.isfile(dest):
            raise ValueError('%s is exist.' % dest)

        path, filename = os.path.split(dest)
        if path and not os.path.exists(path):
            os.makedirs(path)

    def output(self, dest, override, gitlab=False, graph=False):
        """
        导出入口
        :param graph:
        :param dest:
        :param override:
        :param gitlab:
        :return:
        """
        if graph:
            self.output_graph(dest, override)
        else:
            self.output_markdown(dest, override, gitlab)

    def output_graph(self, dest, override):
        """
        生成关系图像
        :param dest:
        :param override:
        :return:
        """
        self.init_path(dest, override)
        generator = self.graph_generator

        _output = list()
        tables = self.get_tables()
        for table in tables:
            table_name = table[0]
            table_info = self.get_table_info(table_name)
            columns = self.get_columns(table_name)

            # 表名
            table_name = table_info.name
            table_comment = ''
            if table.comment:
                table_comment = table_info.comment
            else:
                if table_info.name in self.migration_tables:
                    table_comment = self.migration_tables[table_info.name]
            # 字段输出
            _table_data = {
                'table_name': table.name,
                'table_comment': table_comment,
                # 'columns': ['字段名', '类型', '是否可NULL', '描述'],
                'data': [[column.name, column.field_type, column.if_null, column.comment.replace(os.linesep, '')] for
                         column in columns],
            }
            _output.append(generator.label(**_table_data))

        content = ''.join(_output)

        with open(dest, 'w') as f:
            f.write(content)

    def format_db_graph(self, table, columns):
        """
        :param table:
        :param columns:
        :return:
        """
        generator = self.graph_generator

        _output = list()

        # 表名
        table_name = table.name
        table_comment = ''
        if table.comment:
            table_comment = table.comment
        else:
            if table.name in self.migration_tables:
                table_comment = self.migration_tables[table.name]

        # _output.append("%s %s" % (generator.highline(table.engine), generator.highline(table.collation)))
        # 字段输出
        _table_data = {
            'table_name': table.name,
            'table_comment': table_comment,
            # 'columns': ['字段名', '类型', '是否可NULL', '描述'],
            'data': [[column.name, column.field_type, column.if_null, column.comment.replace(os.linesep, '')] for column
                     in columns],
        }
        _output.append(generator.label(**_table_data))
        return _output

    def output_markdown(self, dest, override, gitlab=False):

        self.init_path(dest, override)

        _output = list()
        tables = self.get_tables()
        for table in tables:
            table_name = table[0]
            table_info = self.get_table_info(table_name)
            columns = self.get_columns(table_name)
            _output.extend(self.format_db_doc(table_info, columns))

        content = (os.linesep * 2).join(_output)

        with open(dest, 'w') as f:
            f.write(content)

    def format_db_doc(self, table, columns):
        """
        封装返回的db 格式
        :param table:
        :param columns:
        :return:
        """
        generator = self.md_generator
        _output = list()

        # 表名
        _output.append(generator.title(table.name, 2))
        if table.comment:
            _output.append(generator.comment(table.comment))
        else:
            if table.name in self.migration_tables:
                _output.append(generator.comment(self.migration_tables[table.name]))
            else:
                _output.append(generator.comment('未备注信息'))

        _output.append("%s %s" % (generator.highline(table.engine), generator.highline(table.collation)))
        # 字段输出
        _table_data = {
            'title': ['字段名', '类型', '是否可NULL', '描述'],
            'data': [[column.name, column.field_type, column.if_null, column.comment.replace(os.linesep, '')] for column
                     in columns],
        }

        if gitlab:
            _output.append('<details>')
            _output.append('<summary>点击展开表结构</summary>')

        _output.append(generator.table(**_table_data))

        if gitlab:
            _output.append('</details>')

        _output.append(os.linesep)

        _output.append(generator.newline())

        return _output


if __name__ == '__main__':

    description = """
        DB自文档化助手 0.1
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('dest', nargs='?', default='', help="指定生成的文件地址 如：app/db.md")
    parser.add_argument('--host', default='localhost', help="数据库地址")
    parser.add_argument('--user', default='root', help="数据库用户名")
    parser.add_argument('--name', default='test', help="数据库名称")

    parser.add_argument('-p', '--password', action='store_true', help="使用数据库密码")
    parser.add_argument('--gitlab', action='store_true', help="支持gitlab的样式")
    parser.add_argument('--graph', action='store_true', help="导出png图片格式")
    parser.add_argument('-f', '--force', action="store_true", help="是否覆盖存在的md文件")
    parser.add_argument('--migration', default='', help="指定migration目录")

    args = parser.parse_args()

    db_host = args.host
    db_name = args.name
    db_user = args.user
    dest = args.dest
    force = args.force
    gitlab = args.gitlab
    graph = args.graph
    migration = args.migration

    if not dest:
        parser.print_help()
        exit()

    if args.password:
        db_password = getpass.getpass()
    else:
        db_password = ''

    try:
        db = DB(db_host, db_user, db_password, db_name)
        if migration:
            db.sync_from_migration(migration)

        db.output(dest, force, gitlab, graph)
    except Exception as e:
        print('Warning: %s' % str(e))
