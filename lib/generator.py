#!/usr/bin/python
# -*- coding: utf-8 -*-
import os


class BaseGenerator:
    """
    生成指定格式的基类
    """
    def __init__(self, data=''):
        """
        传入待处理数据
        """
        self.data = data

    def output(self):
        """
        输出文档
        :param format:
        :return:
        """
        pass


class MDGenerator(BaseGenerator):
    """
    生成MD格式文档
    """

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


class GraghGenerator(BaseGenerator):
    """
    生成Gragh格式文档
    """

    def graph(self, labels, relations):
        """
        graph定义
        :return:
        """
        return """
            digraph model_graph {
              fontname = "Helvetica"
              fontsize = 8
              splines  = true
              
              node [
                fontname = "Helvetica"
                fontsize = 8
                shape = "plaintext"
              ]
            
              edge [
                fontname = "Helvetica"
                fontsize = 8
              ]
              
              %s
              
              %s 
            }
        """

    def field(self, *args):
        """
        字段格式化
        :return:
        """

        fields = []
        for arg in args:
            fields.append("""<TD ALIGN="LEFT" BORDER="0"><FONT FACE="Helvetica ">%s</FONT></TD>""" % arg)

        return """<TR>%s</TR>""" % (''.join(fields),)

    def title(self, name):
        """
        标题格式化
        :param name:
        :return:
        """
        return """<TR><TD COLSPAN="3" CELLPADDING="4" ALIGN="CENTER" BGCOLOR="olivedrab4">
        <FONT FACE="Helvetica Bold" COLOR="white" >%s</FONT>
        </TD></TR>
        """ % name

    def _table_start(self):
        return """<TABLE BGCOLOR="palegoldenrod" BORDER="0" CELLBORDER="0" CELLSPACING="0">"""

    def _table_end(self):
        return """</TABLE>"""

    def label(self, *args, **kwargs):
        """
        :return:
        """

        table_name = kwargs.get('table_name')

        return "mis_models_%s[label = <%s>]" % (table_name, self.table(*args, **kwargs))

    def table(self, *args, **kwargs):
        """
        表格输出作为label输出
        参数需要有tilte,data_list
        :return:
        """
        table_name = kwargs.get('table_name')
        table_comment = kwargs.get('table_comment')
        data = kwargs.get('data')

        if not data or not table_name:
            raise AttributeError('param is empty')

        title = "%s(%s)" % (table_name, table_comment)
        # 字段长度要保持一致
        output = [self._table_start(), self.title(title)]

        for d in data:
            output.append(self.field(*d))
        output.append(self._table_end())
        return os.linesep.join(output)