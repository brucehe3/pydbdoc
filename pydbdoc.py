#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
读取数据库中的信息生成markdown文档
===========================================================================
@Author Bruce He <hebin@comteck.cn>
@Date  2018-05-31
@Version 0.1
"""
import os
import argparse
import pymysql
import getpass
from collections import namedtuple


class MDGenerator:
    """
    生成MD格式文档
    """

    def __init__(self, data=''):
        """
        传入待处理数据
        """
        self.data = data

    def title(self, text, font_size=1):
        """
        返回标题
        :param text:
        :param font_size: 1-5 对应 1-5号标题
        :return:
        """
        if font_size not in (1, 2, 3, 4, 5,):
            raise AttributeError('字号大小不正确')
        return '#' * font_size + ' ' + text

    def bold(self, text):

        return '**%s**' % text

    def comment(self, text):
        return '> %s%s' % (text, os.linesep)

    def highline(self, text):
        return "`%s`" % text

    def code(self, text, code_type=''):

        return """```%s%s%s%s```""" % (code_type, os.linesep, text, os.linesep)

    def newline(self):
        return '---'

    def table(self, *args, **kwargs):
        """
        表格输出
        参数需要有tilte,alignment,data_list
        :return:
        """
        title = kwargs.get('title')
        alignment = kwargs.get('alignment')
        data = kwargs.get('data')

        if not isinstance(data, list) or not isinstance(title, list):
            raise TypeError('param format is error')
        if not data or not title:
            raise AttributeError('param is empty')

        length = len(title)

        if not alignment:
            alignment = [':---'] * length
        # 字段长度要保持一致
        output = [' | '.join(title), ' | '.join(alignment)]
        for d in data:
            data_string = ' | '.join(d)
            if len(d) < length:
                # 要补足
                data_string += ' | ' * (length - len(d))

            output.append(data_string)

        return os.linesep.join(output)

    def output(self):
        """
        输出文档
        :param format:
        :return:
        """
        pass


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

    def output(self, dest, override):

        if not override and os.path.isfile(dest):
            raise ValueError('%s is exist.' % dest)

        path, filename = os.path.split(dest)
        if path and not os.path.exists(path):
            os.makedirs(path)

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

        _output.append("%s %s" % (generator.highline(table.engine), generator.highline(table.collation)))
        # 字段输出
        _table_data = {
            'title': ['字段名', '类型', '是否可NULL', '描述'],
            'data': [[column.name, column.field_type, column.if_null, column.comment] for column in columns],
        }
        _output.append(generator.table(**_table_data))

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
    parser.add_argument('-f', '--force', action="store_true", help="是否覆盖存在的md文件")

    args = parser.parse_args()

    db_host = args.host
    db_name = args.name
    db_user = args.user
    dest = args.dest
    force = args.force

    if not dest:
        parser.print_help()
        exit()

    if args.password:
        db_password = getpass.getpass()
    else:
        db_password = ''

    try:
        db = DB(db_host, db_user, db_password, db_name)
        db.output(dest, force)
    except Exception as e:
        print('Warning: %s' % str(e))
