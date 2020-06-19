# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     doctoexcel
   Description :
   Author :       soliva
   date：          2020/6/18
-------------------------------------------------
   Change Activity:
                   2020/6/18:
-------------------------------------------------
"""


from docx import Document
import pandas as pd
xlsx= 'test.xlsx'
xls = pd.ExcelWriter(xlsx)
word = u'P2006090117_李荣国_ct_panel18_2020.06.19-final.docx'
doc = Document(word)
tables = doc.tables

for i, tb in enumerate(tables):
    mat = []  # 用 list 套 list 的方法装二维表格内容
    for r in range(0, len(tb.rows)):
        row = []
        for c in range(0, len(tb.columns)):
            cell = tb.cell(r, c)
            txt = cell.text if cell.text != '' else ' '  # 无内容用空格占位
            row.append(txt)
        mat.append(row)
    df = pd.DataFrame(mat,columns=mat[0])

    # print df.columns
    # if u"核苷酸\n变化" in df.columns:
    #     print df
    df.to_excel(xls, sheet_name='{i}'.format(**locals()))

xls.save()  # 保存
xls.close()  # 关闭
#
